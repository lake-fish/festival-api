# core/query.py
import re
import requests
from datetime import datetime
from typing import Optional
from lunar_python import Lunar, Solar

from config import settings
from core.cache import cached
from core.models import SolarDate, LunarDate, HolidayInfo


class FestivalQuery:
    """节日查询核心类"""

    # 农历固定节日：{节日名: (农历月, 农历日)}
    LUNAR_FESTIVALS = {
        '春节': (1, 1), '元宵': (1, 15), '龙头节': (2, 2), '花朝节': (2, 12),
        '上巳': (3, 3), '端午': (5, 5), '七夕': (7, 7), '中元': (7, 15),
        '中秋': (8, 15), '重阳': (9, 9), '下元': (10, 15), '腊八': (12, 8),
        '小年': (12, 23), '除夕': (12, 29)  # 除夕特殊处理
    }

    # 公历固定节日：{节日名: (公历月, 公历日)}
    SOLAR_FESTIVALS = {
        '元旦': (1, 1), '情人节': (2, 14), '妇女节': (3, 8), '植树节': (3, 12),
        '愚人节': (4, 1), '劳动节': (5, 1), '青年节': (5, 4), '儿童节': (6, 1),
        '建党节': (7, 1), '建军节': (8, 1), '教师节': (9, 10), '国庆节': (10, 1),
        '万圣节': (10, 31), '光棍节': (11, 11), '平安夜': (12, 24), '圣诞节': (12, 25)
    }

    # 法定节假日（用于查提莫API）
    LEGAL_HOLIDAYS = {'春节', '清明', '劳动节', '端午', '中秋', '国庆', '元旦'}

    # 24节气列表（按时间顺序）
    SOLAR_TERMS = [
        '立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
        '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
        '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
        '立冬', '小雪', '大雪', '冬至', '小寒', '大寒'
    ]

    # 节日别名映射
    ALIASES = {
        '中秋节': '中秋', '端午节': '端午', '重阳节': '重阳',
        '元宵节': '元宵', '腊八节': '腊八', '情人节': '情人节',
        '万圣节前夜': '万圣节', '圣诞夜': '平安夜'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'FestivalQuery/1.0'})

    def _normalize_festival(self, name: str) -> Optional[str]:
        """标准化节日名称"""
        name = name.strip()
        # 先查别名映射
        if name in self.ALIASES:
            return self.ALIASES[name]
        # 检查是否已经是标准名
        all_festivals = set(self.LUNAR_FESTIVALS.keys()) | set(self.SOLAR_FESTIVALS.keys())
        if name in all_festivals:
            return name
        # 模糊匹配（处理"七夕节" -> "七夕"这种情况）
        for festival in sorted(all_festivals, key=len, reverse=True):
            if name.startswith(festival) or festival in name:
                return festival
        return None

    def _parse_year(self, query: str) -> int:
        """解析年份"""
        current = datetime.now().year
        if any(k in query for k in ['今年', '本年', '现在', '当前']):
            return current
        elif any(k in query for k in ['明年', '来年', '下一年']):
            return current + 1
        elif any(k in query for k in ['去年', '上年', '上一年']):
            return current - 1
        # 匹配 "2025年" 格式
        match = re.search(r'(\d{4})\s*年', query)
        return int(match.group(1)) if match else current

    def _parse_festival(self, query: str) -> Optional[str]:
        """解析节日名称"""
        # 先检查别名（按长度降序，避免短名误匹配）
        for alias in sorted(self.ALIASES.keys(), key=len, reverse=True):
            if alias in query:
                return self.ALIASES[alias]
        
        # 再检查标准节日名（按长度降序，避免短名误匹配）
        candidates = list(self.LUNAR_FESTIVALS.keys()) + list(self.SOLAR_FESTIVALS.keys())
        for name in sorted(candidates, key=len, reverse=True):
            if name in query:
                return self._normalize_festival(name)
        return None

    def _parse_solar_term(self, query: str) -> Optional[str]:
        """解析节气名称"""
        # 按长度降序匹配，避免短名误匹配（如"小寒"和"大寒"）
        for term in sorted(self.SOLAR_TERMS, key=len, reverse=True):
            if term in query:
                return term
        return None

    @cached(key_prefix="date_convert", ttl=settings.CACHE_TTL)
    def _convert_lunar_to_solar(self, year: int, month: int, day: int) -> tuple[Solar, Lunar]:
        """农历转公历（带缓存）"""
        # 除夕特殊处理：除夕是农历年的最后一天
        if month == 12 and day == 29:
            try:
                # 先尝试12月30日
                lunar = Lunar.fromYmd(year, 12, 30)
                # 检查是否有效（如果该年没有12月30日，lunar-python可能会返回错误日期）
                if lunar.getMonth() == 12 and lunar.getDay() == 30:
                    return lunar.getSolar(), lunar
            except:
                pass
            # 如果12月30日不存在，使用12月29日
            lunar = Lunar.fromYmd(year, 12, 29)
        else:
            lunar = Lunar.fromYmd(year, month, day)
        return lunar.getSolar(), lunar

    @cached(key_prefix="date_convert", ttl=settings.CACHE_TTL)
    def _convert_solar_to_lunar(self, year: int, month: int, day: int) -> tuple[Solar, Lunar]:
        """公历转农历（带缓存）"""
        solar = Solar.fromYmd(year, month, day)
        return solar, solar.getLunar()

    @cached(key_prefix="solar_term", ttl=settings.CACHE_TTL)
    def _get_solar_term_date(self, year: int, term_name: str) -> Optional[tuple[Solar, Lunar]]:
        """获取指定年份的节气日期"""
        try:
            # 节气表包含该年及前后一年的节气，需要检查多个年份
            # 先检查当前年
            lunar = Lunar.fromYmd(year, 1, 1)
            jie_qi_table = lunar.getJieQiTable()
            solar = jie_qi_table.get(term_name)
            
            if solar and solar.getYear() == year:
                return solar, solar.getLunar()
            
            # 如果不在当前年，检查上一年（某些节气可能在上一年的1月，如大寒）
            lunar_prev = Lunar.fromYmd(year - 1, 1, 1)
            jie_qi_table_prev = lunar_prev.getJieQiTable()
            solar = jie_qi_table_prev.get(term_name)
            if solar and solar.getYear() == year:
                return solar, solar.getLunar()
            
            # 检查下一年（某些节气可能在下一年，但这种情况较少）
            lunar_next = Lunar.fromYmd(year + 1, 1, 1)
            jie_qi_table_next = lunar_next.getJieQiTable()
            solar = jie_qi_table_next.get(term_name)
            if solar and solar.getYear() == year:
                return solar, solar.getLunar()
            
            return None
        except Exception as e:
            return None

    @cached(key_prefix="holiday_info", ttl=settings.CACHE_TTL)
    def _fetch_holiday_info(self, date_str: str) -> Optional[HolidayInfo]:
        """调用提莫API查放假信息"""
        try:
            url = f"{settings.TIMOR_API_BASE}/info/{date_str}"
            resp = self.session.get(url, timeout=settings.REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if data.get('holiday'):
                h = data['holiday']
                return HolidayInfo(
                    is_legal=True,
                    name=h.get('name'),
                    rest_days=h.get('rest'),
                    wage=h.get('wage'),
                    note=h.get('note')
                )
            return HolidayInfo(is_legal=False, note='非法定节假日')
        except Exception as e:
            return HolidayInfo(is_legal=False, note=f'查询失败: {str(e)}')

    def _build_solar_date(self, solar: Solar) -> SolarDate:
        return SolarDate(
            date=solar.toYmd(),
            year=solar.getYear(),
            month=solar.getMonth(),
            day=solar.getDay(),
            week=solar.getWeek(),
            week_cn=solar.getWeekInChinese()
        )

    def _build_lunar_date(self, lunar: Lunar) -> LunarDate:
        month_cn = lunar.getMonthInChinese()
        # 判断是否是闰月：月份名称中包含"闰"字
        is_leap = '闰' in month_cn
        return LunarDate(
            date_cn=f"{month_cn}月{lunar.getDayInChinese()}",
            year=lunar.getYear(),
            month=lunar.getMonth(),
            day=lunar.getDay(),
            year_ganzhi=lunar.getYearInGanZhi(),
            month_cn=month_cn,
            day_cn=lunar.getDayInChinese(),
            is_leap=is_leap
        )

    def query(self, question: str, check_holiday: bool = True) -> dict:
        """主查询方法"""
        # 1. 解析输入
        year = self._parse_year(question)
        
        # 2. 先尝试解析节气
        solar_term = self._parse_solar_term(question)
        if solar_term:
            term_result = self._get_solar_term_date(year, solar_term)
            if term_result:
                solar, lunar = term_result
                result = {
                    'success': True,
                    'festival': solar_term,
                    'query_year': year,
                    'festival_type': 'solar_term',
                    'solar': self._build_solar_date(solar),
                    'lunar': self._build_lunar_date(lunar),
                }
                # 清明是法定节假日
                if check_holiday and solar_term == '清明':
                    result['holiday'] = self._fetch_holiday_info(solar.toYmd())
                result['text'] = self._format_text(result)
                return result
            else:
                raise ValueError(f"未找到{year}年的{solar_term}节气日期")
        
        # 3. 解析节日
        festival = self._parse_festival(question)
        if not festival:
            raise ValueError(f"未识别到节日或节气，支持: {', '.join(list(self.LUNAR_FESTIVALS.keys())[:5])}... 或24节气")

        # 4. 日期转换
        if festival in self.LUNAR_FESTIVALS:
            # 农历节日 → 转公历
            lm, ld = self.LUNAR_FESTIVALS[festival]
            solar, lunar = self._convert_lunar_to_solar(year, lm, ld)
            festival_type = "lunar_fixed"
        else:
            # 公历节日 → 转农历
            sm, sd = self.SOLAR_FESTIVALS[festival]
            solar, lunar = self._convert_solar_to_lunar(year, sm, sd)
            festival_type = "solar_fixed"

        # 5. 构建基础响应
        result = {
            'success': True,
            'festival': festival,
            'query_year': year,
            'festival_type': festival_type,
            'solar': self._build_solar_date(solar),
            'lunar': self._build_lunar_date(lunar),
        }

        # 6. 查询节假日信息（可选）
        if check_holiday and festival in self.LEGAL_HOLIDAYS:
            result['holiday'] = self._fetch_holiday_info(solar.toYmd())

        # 7. 生成友好文本
        result['text'] = self._format_text(result)

        return result

    def _format_text(self, data: dict) -> str:
        """生成友好回复文本"""
        festival_type = data.get('festival_type', '')
        if festival_type == 'solar_term':
            lines = [f"🌿 {data['festival']}"]
        else:
            lines = [f"🎊 {data['festival']}"]
        
        lines.append(f"📅 公历：{data['solar'].date}（星期{data['solar'].week_cn}）")
        lines.append(f"🌙 农历：{data['lunar'].year_ganzhi}年 {data['lunar'].date_cn}")

        if data.get('holiday'):
            h = data['holiday']
            if h.is_legal:
                lines.append(f"✅ 法定节假日：{h.name}")
                if h.rest_days:
                    lines.append(f"📆 放假{h.rest_days}天")
                if h.wage:
                    lines.append(f"💰 加班工资：{h.wage}倍")
            elif h.note and '非法定' in h.note:
                lines.append("ℹ️ 传统节日（当年不放假）")

        return '\n'.join(lines)