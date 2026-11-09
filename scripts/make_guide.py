# -*- coding: utf-8 -*-
"""產出「社工師備考指南」Word 檔：14pt、純黑白"""
import os, datetime

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

import stats

from paths import DOCS, APP

OUT = os.path.join(DOCS, '社工師備考指南_十年考古題分析.docx')
FONT = '微軟正黑體'
TODAY = datetime.date(2026, 11, 9)
EXAM1 = datetime.date(2027, 2, 20)

import glob as _glob, json as _jj
_HERE = os.path.dirname(os.path.abspath(__file__))
_QS = _jj.load(open(os.path.join(_HERE, '..', 'build', 'questions.json'), encoding='utf-8'))
_QID = lambda q: '%s|%s|%d' % (q['exam'], q['subject'], q['no'])
_BYID = {_QID(q): q for q in _QS}
LAWFIX = {}
for _f in sorted(_glob.glob(os.path.join(_HERE, 'lawfix', '*.json'))):
    LAWFIX.update(_jj.load(open(_f, encoding='utf-8')))
MOCK = []
for _f in sorted(_glob.glob(os.path.join(_HERE, 'mock', 'm*.json'))):
    MOCK.extend(_jj.load(open(_f, encoding='utf-8')))
_LIVE5 = ['社會工作', '社會工作直接服務', '社會政策與社會立法', '人類行為與社會環境', '社會工作研究方法']
FIRST_POOL = sum(1 for q in _QS if q['subject'] in _LIVE5 and _QID(q) not in LAWFIX)


def mock_kind(b):
    if b.startswith('易混'):
        return '易混陷阱'
    if b.startswith('時事'):
        return '時事'
    if b.startswith('近五年'):
        return '近五年高頻考點'
    return '新法'


doc = Document()

# ── 版面與預設字型 ────────────────────────────
sec = doc.sections[0]
sec.top_margin = sec.bottom_margin = Cm(2.2)
sec.left_margin = sec.right_margin = Cm(2.4)

st = doc.styles['Normal']
st.font.name = FONT
st.font.size = Pt(14)
st.font.color.rgb = RGBColor(0, 0, 0)
st._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.4


def _fix(run, size=14, bold=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    return run


def para(text='', size=14, bold=False, align=None, after=6, indent=0):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    _fix(p.add_run(text), size, bold)
    return p


def h1(text):
    para('', after=2)
    p = para(text, size=17, bold=True, after=8)
    return p


def h2(text):
    return para(text, size=15, bold=True, after=4)


def bullet(text, indent=0.6):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(indent)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.4
    _fix(p.add_run('・' + text))
    return p


def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, htxt in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ''
        _fix(c.paragraphs[0].add_run(htxt), 13, True)
        c.paragraphs[0].paragraph_format.space_after = Pt(2)
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = ''
            _fix(cells[i].paragraphs[0].add_run(str(v)), 13)
            cells[i].paragraphs[0].paragraph_format.space_after = Pt(2)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ══ 封面 ══════════════════════════════════
para('專門職業及技術人員高等考試', size=14, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
para('社會工作師　備考指南', size=24, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
para('十年考古題（106–115 年）資料分析版', size=14,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
para('115 年 11 月更新版', size=14, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=18)

days = (EXAM1 - TODAY).days
para('製作日期：%d 年 %d 月 %d 日' % (TODAY.year, TODAY.month, TODAY.day), size=13,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
para('距 116 年第一次考試（116/02/20）尚有 %d 天' % days, size=13,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
para('分析母體：106–115 年共 20 次考試、115 份考卷、4,600 題測驗題、230 題申論題',
     size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=18)

para('這份指南做什麼用', size=15, bold=True, after=4)
para('市面上的考古題整理多半止於「題目與答案」。這份指南把考選部公布的十年試題全部'
     '解析成結構化資料後，統計出各科真正反覆出現的考點，讓準備方向有數字依據，'
     '而不是憑印象。所有數字都可以回推到原始試卷查證。', after=6)
para('搭配線上刷題本使用效果最好：指南負責「先看清楚地圖」，刷題本負責「每天走路」。', after=10)

para('本版更新重點', size=15, bold=True, after=4)
bullet('刷題本 4,600 題測驗題全部附解析：為什麼對、其他選項錯在哪、相關法條連結')
bullet('寫過的題目不再重複出現，隨機出題只出新題；答錯的收進錯題本另外複習')
bullet('修法題 %d 題不再出題，逐題對照現行條文給出現在的答案（第三章，含答案已改變的題目一覽）' % len(LAWFIX))
bullet('新增自編模擬試題 %d 題：依 111–115 年出題趨勢、時事、新法與個人錯題出題（第七章）' % len(MOCK))
bullet('讀書時程改為「第一輪限期刷完」的算法，依剩餘天數重排（第五章）')
bullet('法規數字速記表更正一處條號：特殊境遇家庭扶助條例的傷病醫療補助為第 9 條')

doc.add_page_break()

# ══ 一、考試制度 ══════════════════════════
h1('一、考試制度速覽')

h2('（一）應考資格')
para('須自國內外專科以上學校社會工作相關科系所畢業，領有畢業證書，並符合下列修課要求：', after=4)
bullet('修畢五大領域共 15 學科、45 學分以上（每科最多採計 3 學分）')
bullet('曾修習社會工作（福利）實習或實地工作學分')
para('五大領域及其學科數：', after=3)
table(['領域', '學科數', '包含科目'],
      [['社會工作概論', '2', '社會工作概論；社會福利概論或社會工作倫理'],
       ['社會工作直接服務方法', '3', '社會個案工作；社會團體工作；社區工作或社區組織與發展'],
       ['人類行為與社會環境', '4', '人類行為與社會環境；社會學；心理學；社會心理學'],
       ['社會政策立法與行政管理', '4', '社會政策與社會立法；社會福利行政；方案設計與評估；社會工作管理或非營利組織管理'],
       ['社會工作研究法', '2', '社會工作研究法或社會研究法；社會統計']],
      widths=[4.2, 1.8, 9.5])
para('註：資格認定以考選部公告之考試規則與應考資格審查為準，修課名稱有疑義者'
     '應於報名前向考選部確認。', size=12, after=10)

h2('（二）應試科目（115 年起）')
para('考試院於 114 年 6 月 6 日修正發布，自 115 年第一次考試起刪除普通科目'
     '「國文（作文）」及專業科目「社會工作管理」，現行為 5 科專業科目：', after=4)
table(['應試科目', '題型配置'],
      [['社會工作', '申論題 2 題 40 分＋測驗題 40 題 60 分'],
       ['社會工作直接服務', '申論題 2 題 40 分＋測驗題 40 題 60 分'],
       ['社會政策與社會立法', '申論題 2 題 40 分＋測驗題 40 題 60 分'],
       ['人類行為與社會環境', '申論題 2 題 40 分＋測驗題 40 題 60 分'],
       ['社會工作研究方法', '申論題 2 題 40 分＋測驗題 40 題 60 分']],
      widths=[6.0, 9.5])
para('測驗題為單一選擇題，每題 1.5 分，40 題共 60 分；申論題 2 題各 20 分，共 40 分。'
     '每科考試時間 2 小時。', size=12, after=10)

h2('（三）及格標準')
para('應試科目總成績滿 60 分為及格。現制無普通科目，總成績即 5 科專業科目平均成績。', after=3)
bullet('任一科成績為零分者，不予及格')
bullet('專業科目平均成績未滿 50 分者，不予及格')
bullet('缺考之科目視為零分')
para('實務上的意義：這是「平均 60 分」而非「每科 60 分」，強科可以拉抬弱科；'
     '但弱科不能崩盤，一科考壞就要靠其他四科補回來，風險很高。'
     '因此配分策略應該是「把最弱的一科先拉到 55 分以上」，而不是把強科從 75 分推到 85 分。', after=10)

h2('（四）116 年考試日程')
table(['梯次', '報名期間（民國）', '考試日期（民國）'],
      [['116 年第一次', '115/10/20 – 10/29', '116/02/20 – 02/21'],
       ['116 年第二次', '116/04/13 – 04/22', '116/07/31 – 08/03']],
      widths=[3.8, 5.6, 5.6])
para('考區：臺北、新竹、臺中、臺南、高雄、花蓮、金門。'
     '日程以考選部公告之考試期日計畫表為準，報名前請再確認一次。', size=12, after=4)
para('提醒：116 年第一次考試的報名期間已於 115/10/29 截止。'
     '若沒有報到第一次，目標請改為第二次（報名 116/04/13 起），第五章另附第二次的時程。', size=12)

doc.add_page_break()

# ══ 二、十年數據 ══════════════════════════
h1('二、十年考古題告訴我們什麼')

para('以下統計來自 106–115 年全部 115 份考卷、4,600 題測驗題。'
     '「考點」是依題幹與選項用詞自動歸類的結果（共 158 個考點，可歸類率約 76%），'
     '不是考選部的官方分類，但足以看出命題重心。', after=8)

h2('（一）十年來，這些是真正反覆考的')
para('「份數」是指這個考點在 20 次考試的該科考卷中，有幾份出現過——'
     '份數越高代表越穩定，幾乎每年都會碰到，優先度高於單純的題數多寡。', size=12, after=6)

SUB_NOTE = {
 '社會工作': '增權／充權相關概念合計近 110 題、20 份考卷全中，是本科第一重點。'
             '倫理（保密、案主自決、倫理兩難）合計約 75 題，務必背熟 Reamer 倫理抉擇原則與倫理守則條文。',
 '社會工作直接服務': '社區工作佔比異常高（107 題、20 份全中），遠超一般人對「直接服務＝個案」的印象，'
                     '是最容易失分的盲區；團體工作階段（51 題）次之。',
 '社會政策與社會立法': '幾乎所有重點考點都是「19 份考卷出現」——這科最像背科，'
                       '社會救助、兒少、身障三大法規合計近 250 題，法條數字（金額、年限、年齡）務必精確。',
 '人類行為與社會環境': '發展理論四大家（Piaget、Erikson、Freud、Kohlberg）與生命週期各階段是骨幹，'
                       '青少年期單獨就 89 題，是最高頻的單一階段。',
 '社會工作研究方法': '質性研究方法 127 題、19 份全中，是本科最大單一考點；'
                     '抽樣、統計、測量層次合計 236 題。這科最吃「觀念清楚」，投報率最高。',
}

tops = stats.top_by_subject(12)
for s in stats.LIVE:
    h2('◆ ' + s)
    table(['考點', '題數', '出現份數'],
          [[n, str(c), '%d 份' % p] for n, c, p in tops[s]],
          widths=[8.5, 3.0, 3.5])
    para(SUB_NOTE[s], size=12, after=10)

h2('（二）申論題的主題分布')
para('十年 230 題申論題中，可歸類主題的前段如下。申論題重視整合與實務應用，'
     '同一主題會以不同情境反覆出現，準備時應以「主題」為單位備妥架構，而非背單題。', after=4)
et = stats.essay_top(12)
table(['申論主題', '題數'], [[n, str(c)] for n, c in et], widths=[10.5, 4.5])

h2('（三）跨年度重複出現的題目')
reps = stats.repeats()
para('十年間有 %d 組題目的題幹完全相同、跨不同年度重複出現。'
     '數量不多，但代表考選部確實會重複命題，把考古題刷熟是有直接報酬的。' % len(reps), after=4)
for stem, exams in reps[:6]:
    bullet('%s（%s）' % (stem[:40] + ('…' if len(stem) > 40 else ''), '、'.join(exams)))

doc.add_page_break()

# ══ 二之二、法規時效 ══════════════════════
h1('三、法規已修正的考古題，不要硬背')

para('這是準備社會政策與社會立法最容易踩的坑：考古題的「正確答案」是當年條文，'
     '法條修正後就不再是正確答案，照背反而有害。', after=6)

_cnt = {'same': 0, 'changed': 0, 'void': 0}
for _v in LAWFIX.values():
    _cnt[_v['status']] += 1
para('我們把題庫中明確引用法規名稱的題目，逐一比對該法規的最新修正日期，'
     '找出出題後法規又修正過的題目共 %d 題，再逐題對照全國法規資料庫的現行條文，'
     '判斷「依現在的法律，答案是什麼」。結果如下：' % len(LAWFIX), after=4)
table(['結果', '題數', '怎麼準備'],
      [['現行答案不變', str(_cnt['same']), '修法沒動到被考的內容，照原答案記即可'],
       ['答案已改變', str(_cnt['changed']), '照下表的現行答案記，舊答案不要背'],
       ['現行法下題目不成立', str(_cnt['void']), '四個選項已無法對應現行規定，直接記新規定']],
      widths=[4.6, 1.8, 9.0])
para('這 %d 題在線上刷題本不再出題（刷題、測驗、隨機都不會抽到），'
     '改放在選單的「修法題」頁，直接列出現行答案、說明與現行法條連結，可依法規篩選。'
     '本章與該頁內容僅供參考，不負法律責任；法規會再修正，請以現行條文為準。' % len(LAWFIX), size=12, after=8)

h2('答案已改變、題目不成立的題目一覽')
_ST = {'changed': '答案改變', 'void': '題目不成立'}
_rows = []
for _k, _v in LAWFIX.items():
    if _v['status'] == 'same':
        continue
    _q = _BYID[_k]
    _stem = _q['stem'][:34] + ('…' if len(_q['stem']) > 34 else '')
    _rows.append(['%s\n第 %d 題' % (_q['exam'], _q['no']), _stem,
                  '%s\n%s' % (_ST[_v['status']],
                               ('當年 %s → 現在 %s' % (_q['answer'], _v['current'])) if _v['status'] == 'changed'
                               else '當年 %s' % _q['answer']),
                  _v['law']])
table(['考試', '題目（節錄）', '答案', '現行法條'], _rows, widths=[2.8, 6.2, 3.2, 3.2])

h2('這些修法變動最常被考，請直接記現行規定')
for _k, _v in LAWFIX.items():
    if _v['status'] != 'same':
        bullet(_v['now'])
para('', after=6)

h2('已核對的 24 部法規')
from lawcheck import LAWS
import json as _json, collections as _c
_mc = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', 'build', 'questions.json'), encoding='utf-8'))
_hit = _c.Counter()
for _q in _mc:
    for _n in (_q.get('stale') or []):
        _hit[_n] += 1
_RK = {'high': '高風險', 'mid': '留意', 'low': '影響小', 'none': '無影響'}
_rows = sorted(LAWS.items(), key=lambda kv: (-{'high':3,'mid':2,'low':1,'none':0}[kv[1]['risk']],
                                             -_hit[kv[0]]))
table(['法規名稱', '最新修正', '修正範圍', '級別', '題數'],
      [[k, str(v['amended'])[:3] + '/' + str(v['amended'])[3:5] + '/' + str(v['amended'])[5:],
        v['scope'], _RK[v['risk']], ('%d' % _hit[k]) if _hit[k] else '—']
       for k, v in _rows],
      widths=[4.6, 2.3, 5.4, 1.6, 1.3])
para('修正日期與條文範圍於 115 年 9 月 23 日逐條查自全國法規資料庫沿革（law.moj.gov.tw）。', size=12, after=8)

h2('特別要注意的三件事')
bullet('性別工作平等法已於 112/08/16 修正並更名為「性別平等工作法」，'
       '同日性騷擾防治法亦大幅修正，職場性騷擾的處理流程與雇主義務均有變動。'
       '112 年第二次以前的相關考題，名稱與程序都要重新確認。')
bullet('精神衛生法 111/12/14 全文修正，但施行日期為公布後二年（113/12/14）。'
       '意思是舊制考題在 113 年底前仍然有效，之後才失效——這種「修正與施行分離」的情況最容易搞錯。')
bullet('身心障礙者權益保障法與老人福利法雖然都在 114/08/01 修正，但分別只改了第 53 條與第 48 條。'
       '兩法合計 79 題觸及修法，逐題核對後多數答案不變；'
       '但老人福利法第 41 條保護安置費用改為 60 日內返還、償還對象擴及配偶，相關題目答案已改變。')

h2('實務做法')
bullet('刷題本已自動排除修法題，刷題時不用再分辨哪題過時；考前把「修法題」頁從頭看一遍')
bullet('考前一個月，把這 24 部法規的現行條文各看一遍，特別是數字（天數、時數、年齡、人數、比例），'
       '可直接用下一節的「法規數字速記表」')
bullet('若在其他考古題書或網站看到這些題目，以本章與「修法題」頁的現行答案為準，不要照當年答案背')
bullet('這份清單有時效。法規隨時可能再修，報名前請上全國法規資料庫再確認一次')

h2('法規數字速記表')
from lawnums import NUMS, CHECKED as _NC
para('測驗題最愛考數字。十年題庫的社會政策與社會立法 760 題中，有 206 題（27%）的選項就是在比'
     '天數、時數、年齡、人數或金額，而且常用「把數字改掉」的錯誤選項出題。'
     '申論題寫出正確數字與條號，也是閱卷最容易辨認的得分點。', after=4)
para('下表每一項均於 115 年 9 月 24 日逐條查自全國法規資料庫現行條文。'
     '研究方法與人類行為的「學理」項目沒有條號，依據是考選部公告的正確答案，出處欄標示年次。'
     '「常考陷阱」欄是題庫中實際出現過的錯誤寫法。'
     '本表僅供參考，不負法律責任；法規會再修正，數字以現行條文為準。', size=12, after=6)
table(['法規／科目', '項目', '現行規定', '條號／出處', '常考陷阱'],
      [[n[0], n[1], n[2], n[3], n[4] or '—'] for n in NUMS],
      widths=[2.9, 2.6, 4.6, 1.8, 3.3])

h2('通報時限一次記')
bullet('兒少權法第 53 條、家暴法第 50 條、性侵害犯罪防治法第 11 條、身障法第 76 條、'
       '兒少性剝削條例第 7 條：責任通報一律「立即、至遲不得超過 24 小時」。')
bullet('老人福利法第 43 條例外：本法只寫主管機關接獲通報後「應立即處理」，'
       '通報時限授權由「通報及處理辦法」另定。本法與子法的差別是考點。')
bullet('緊急安置一律 72 小時（兒少權法第 56 條、身障法第 80 條、兒少性剝削條例第 16 條），'
       '繼續安置以 3 個月為限、每次得延長 3 個月。家暴法的緊急保護令則是 4 小時內核發，不要混。')

doc.add_page_break()

# ══ 四、各科策略 ══════════════════════════
h1('四、各科準備策略')

STRAT = [
 ('社會工作研究方法', '最優先，投報率最高',
  ['科目本身是方法論，觀念通了就穩定得分，不像法規會逐年修正。',
   '主攻順序：質性研究方法 → 抽樣 → 測量層次與量表 → 效度／信度 → 統計分析。',
   '統計題不需要會算，重點在「看得懂數據在說什麼」：t 檢定、變異數分析、相關與迴歸各自回答什麼問題、p 值代表什麼。',
   '把十年 760 題刷過兩輪，這科通常可以穩定在 70 分以上，用來拉抬平均。']),
 ('社會政策與社會立法', '最需要時間，但最不能放掉',
  ['本科是純記憶量最大的一科，且幾乎每個重點考點都是 19 份考卷全中，沒有僥倖空間。',
   '以法規為單位整理：社會救助法、兒少權法、身障權益保障法、家暴防治法、性侵害防治法、老人福利法、長照法。',
   '特別注意數字：給付金額、年齡界線、期限天數、比率——考題最愛在這裡設陷阱。',
   '法規每年可能修正，作答以現行條文為準；十年前的舊題若條文已修，請以新法核對後再記。']),
 ('社會工作直接服務', '注意社區工作這個盲區',
  ['多數人把重心放在個案工作，但十年數據顯示社區組織與發展高達 107 題、每一份考卷都考。',
   '三大方法（個案、團體、社區）務必平均分配時間，不要偏食。',
   '團體工作的發展階段、團體類型、領導技巧是穩定考點。',
   '會談技巧題多為情境題，背定義沒用，要練「看情境選反應」。']),
 ('人類行為與社會環境', '架構清楚就好拿分',
  ['以「理論家 × 生命階段」建一張二維表：Erikson、Freud、Piaget、Kohlberg 各階段的名稱、年齡、任務、危機。',
   '青少年期（89 題）與老年期（55 題）是兩個高峰，優先熟讀。',
   '生態系統觀點（微視／中介／外部／鉅視／時間系統）務必能舉例區辨。',
   '心理疾病與精神健康近年比重上升，DSM 常見診斷的基本特徵要有印象。']),
 ('社會工作', '概念層面最廣，靠考古題建立手感',
  ['涵蓋專業史、價值倫理、理論模式、角色功能，範圍最散。',
   '增權／充權相關概念合計近 110 題，是單一最大考點群，務必能區辨增權、優勢觀點、倡導三者。',
   '倫理題必考：Reamer 倫理抉擇六原則、社會工作師倫理守則、保密例外與通報義務。',
   '慈善組織會社與睦鄰組織運動的對照是經典送分題，不要丟。']),
]

for name, tag, pts in STRAT:
    h2('◆ %s ——%s' % (name, tag))
    for x in pts:
        bullet(x)
    para('', after=6)

doc.add_page_break()

# ══ 四、時程 ══════════════════════════════
h1('五、讀書時程')

para('以下兩個版本可依實際可用時間擇一。共同原則：'
     '前段求廣（把題庫刷過一輪），中段求深（錯題依考點打掃），後段求穩（整卷計時模擬）。', after=8)

def _md(d):
    return '%d/%d' % (d.month, d.day)


_D = datetime.timedelta
_f1 = TODAY + _D(days=30)
_f2 = _f1 + _D(days=42)
_wk = EXAM1 - _D(days=7)
h2('（一）%d 天版（現在起至 116 年第一次考試 2/20）' % days)
para('五科扣掉修法題後共 %s 題考古題。原則是「第一輪限期刷完」：先在 30 天內把每一題都寫過一次，'
     '寫過的題目刷題本不會再出，之後只練錯題與模擬題。' % format(FIRST_POOL, ','), size=12, after=4)
table(['每週讀書天數', '30 天內刷完，每個讀書日要寫', '以 1 分鐘 1 題估算'],
      [['7 天', '約 %d 題' % -(-FIRST_POOL // 30), '約 %.1f 小時' % (FIRST_POOL / 30 / 60)],
       ['6 天', '約 %d 題' % -(-FIRST_POOL // 26), '約 %.1f 小時' % (FIRST_POOL / 26 / 60)],
       ['5 天', '約 %d 題' % -(-FIRST_POOL // 21), '約 %.1f 小時' % (FIRST_POOL / 21 / 60)]],
      widths=[3.6, 6.2, 5.6])
para('說實話，30 天刷完對在職者負擔很重。若每天只有 1–1.5 小時，請在刷題本「備考規劃」'
     '把「第一輪幾天內刷完」改成 45 或 60 天，並優先刷研究方法與社會政策兩科；'
     '後面的階段跟著縮短，模擬卷改成每科只做一份。', size=12, after=6)
table(['期間', '階段', '做法'],
      [['%s – %s\n（30 天）' % (_md(TODAY), _md(_f1)), '第一輪刷完',
        '「刷題」選科目、出題方式隨機，寫過的不會重複；\n'
        '每題看完解析再往下，答錯自動進錯題本'],
       ['%s – %s\n（6 週）' % (_md(_f1 + _D(days=1)), _md(_f2)), '錯題強化',
        '「錯題複習」把錯題再刷兩輪；「錯題筆記」逐考點看；\n'
        '「模擬試題」→「依我的錯題考點」練同考點新題；\n每週手寫 2 題申論'],
       ['%s – %s\n（約 4 週）' % (_md(_f2 + _D(days=1)), _md(_wk)), '整卷模擬',
        '每科 2 份模擬卷（40 題、計時 60 分鐘），共 10 份，\n'
        '每週 2–3 份；記錄分數，弱科回頭補錯題'],
       ['%s – %s\n（考前一週）' % (_md(_wk + _D(days=1)), _md(EXAM1)), '只看不寫',
        '錯題筆記、「法規數字」頁、「修法題」頁各看一遍，\n不做新題']],
      widths=[3.6, 2.8, 9.0])

h2('（二）改考 116 年第二次（7/31）')
_e2 = datetime.date(2027, 7, 31)
para('距第二次考試約 %d 天，時間寬裕，建議第一輪放寬為 90 天（每週 5 天約每天 %d 題，約 1 小時）。'
     % ((_e2 - TODAY).days, -(-FIRST_POOL // 64)), size=12, after=4)
table(['期間', '做法'],
      [['%s – 116/2 月上旬' % _md(TODAY), '第一輪 90 天刷完；每週固定一天看錯題筆記'],
       ['116/2 月中 – 5 月', '錯題二刷、三刷；依錯題考點練模擬題；申論題每週 2 題，依主題整理答題骨架'],
       ['116/6 月 – 7/24', '整卷模擬每週 2–3 份；法規數字與修法題頁反覆看'],
       ['考前一週', '只看錯題筆記與法條，不做新題']],
      widths=[4.2, 11.2])
para('第二次考試的報名期間為 116/04/13 – 04/22，記得報名。', size=12, after=6)

h2('（三）每週固定動作')
bullet('週一至週五：每天固定時段刷題，寧可每天 30 分鐘，不要週末補 5 小時')
bullet('每週挑一天：把該週錯題筆記從頭看一遍（不重做，只看）')
bullet('每週手寫 2 題申論：手寫，計時 25 分鐘，寫在紙上而非打字')
bullet('每月一次：做一份整卷計時，記錄分數走勢')

doc.add_page_break()

# ══ 五、申論題 ══════════════════════════
h1('六、申論題怎麼練')

para('申論題佔每科 40 分，是拉開差距的關鍵。考選部不公布標準答案，'
     '也不公布評分標準，因此練習重點不在「背出正確答案」，而在「寫出閱卷者找得到的架構」。', after=8)

h2('（一）配分與時間')
bullet('每科 2 題、各 20 分，合計 40 分')
bullet('每科考試 2 小時，測驗題 40 題約需 40–50 分鐘，申論題可分配 60–70 分鐘')
bullet('平均每題 30 分鐘，其中審題與列大綱 5 分鐘、書寫 25 分鐘')

h2('（二）答題架構（通用四段）')
bullet('第一段：定義與概念——把題目問到的名詞先界定清楚，這段幾乎一定有分')
bullet('第二段：理論依據——指出所依據的觀點或模式，能點出學者姓名更好')
bullet('第三段：分項回答——依題目的小題順序作答，用（一）（二）（三）分點，不要寫成一整段')
bullet('第四段：連結情境——回到題目給的案例或臺灣實務脈絡，這段是高低分的分水嶺')

h2('（三）常見失分')
bullet('沒有依小題順序作答，閱卷者找不到你回答了哪一小題')
bullet('只寫定義不寫應用，題目問「如何處遇」卻通篇在解釋理論')
bullet('字數失衡，第一題寫滿兩頁、第二題只寫半頁')
bullet('字跡潦草。手寫練習就是在練這件事，用電腦打字練不到')

h2('（四）用十年題庫練')
para('230 題申論題已依主題歸類，同主題的題目一次看完，會發現問法高度重複。'
     '建議做法：同一主題抓 3–4 題一起看，整理出一份共用的答題骨架，'
     '之後不論怎麼問都能套用。刷題本的申論題區有作答空間與計時，可直接在上面擬答。', after=6)

doc.add_page_break()

# ══ 六、刷題本 ══════════════════════════
h1('七、線上刷題本怎麼用')

para('題庫網址已另行提供。以下是各功能對應到備考流程的哪個階段：', after=6)
table(['功能', '什麼時候用', '做什麼'],
      [['刷題（練習）', '第一輪', '選科目，答完立即看解析、其他選項錯在哪、法條連結；\n寫過的題目不再重複出'],
       ['錯題複習', '強化期', '只出錯題本的題目，重練到會為止'],
       ['考點複習', '打底期、衝刺期', '點任一考點，看完該主題十年所有題目'],
       ['錯題筆記', '強化期', '錯題依考點聚合，同時帶出同主題其他考題；\n可複製全文貼進 Word'],
       ['測驗模式', '模擬期', '整卷計時、作答完才公布，校正節奏'],
       ['模擬試題', '強化期、模擬期', '自編新題：每科 2 份計時模擬卷，\n或依自己的錯題考點出題'],
       ['修法題', '考前', '法規改過的考古題，直接看現行答案，不出題'],
       ['法規數字', '考前', '易混數字依數字或依法規歸類，例如「24 小時」的規定放在一起'],
       ['申論題', '全期', '題目原文＋擬答空間，自動存檔'],
       ['備考規劃', '每天', '倒數天數、第一輪期限與每日題數、時間不夠時會提醒'],
       ['題庫搜尋', '隨時', '輸入關鍵字，找出所有相關考題'],
       ['學者理論', '打底期', '依出題次數看學者與理論，一鍵練相關題'],
       ['時事', '衝刺期', '近兩年修法與政策，附考試連結與來源']],
      widths=[3.2, 3.6, 8.2])

h2('自編模擬試題')
_mk = {}
_ms = {}
for _x in MOCK:
    _mk[mock_kind(_x['basis'])] = _mk.get(mock_kind(_x['basis']), 0) + 1
para('共 %d 題，五科各 80 題左右，出題比例依 111–115 年各考點實際出題次數分配。'
     '每題附答案、解析與「出題依據」，法規題的條號與數字均對照全國法規資料庫現行條文。' % len(MOCK), after=4)
table(['出題依據', '題數', '說明'],
      [['近五年高頻考點', str(_mk.get('近五年高頻考點', 0)), '111–115 年反覆出現的考點，換題型、換情境再出'],
       ['易混陷阱', str(_mk.get('易混陷阱', 0)), '學者張冠李戴、相近法條數字、相似概念的區辨'],
       ['時事', str(_mk.get('時事', 0)), '近兩年政策與社會事件結合考點，例如社安網、長照、兒少保護'],
       ['新法', str(_mk.get('新法', 0)), '112 年以後新制定或修正的法規']],
      widths=[3.8, 1.8, 9.8])
para('注意：模擬試題是 AI 依資料自編，不是考選部試題，也沒有經過人工逐題審閱。'
     '少數學者理論的譯名或分類，各教科書說法不一，遇到和課本不同時以課本與考古題為準。', size=12, after=10)

para('使用提醒：作答紀錄、錯題本與申論草稿都存在「各人自己的瀏覽器」裡，'
     '換裝置或清除瀏覽資料會消失，也不會互相干擾。'
     '若要保存錯題筆記，請用「複製全文」貼到自己的檔案中。', size=12, after=10)


doc.add_page_break()

# ══ 八、學者與理論 ══════════════════════
import json as _json
_js = open(os.path.join(APP, 'questions.js'), encoding='utf-8').read()
_db = _json.loads(_js[_js.index('{'):_js.rindex('}') + 1])
h1('八、學者與理論（依十年出題次數）')
para('下表只收 106–115 年考題實際出現過的學者，次數由題幹、選項與申論全文自動比對，'
     '選項只列出名稱的題目也會計入。本指南不列「出題老師」：考選部不公布命題委員，'
     '試題依典試法以密件處理，坊間說法無法查證。', after=8)
_rows = []
for sc in _db['scholars']:
    ys = sorted({_db['exams'][_db['rows'][i][0]][:3] for i in sc[7]} |
                {_db['exams'][_db['ess'][i][0]][:3] for i in sc[8]})
    _rows.append([sc[0] + '\n' + sc[1], sc[2], sc[3],
                  '測驗 %d\n申論 %d' % (len(sc[7]), len(sc[8])), '、'.join(ys)])
table(['學者', '科目', '理論', '次數', '出題年度'], _rows, widths=[3.6, 2.8, 3.8, 1.8, 3.0])

h2('理論重點')
for sc in _db['scholars']:
    para(sc[0] + '（' + sc[1] + '）— ' + sc[3], bold=True, after=2)
    for pt in sc[4]:
        bullet(pt)
    para('代表著作：' + '、'.join('《%s》（%s）' % (w[0], w[1]) for w in sc[5]), after=8)

doc.add_page_break()

# ══ 九、時事 ═════════════════════════════
h1('九、時事與政策動態')
para('申論題常要求結合臺灣現況。以下 %d 則整理於 %s，摘要為自行改寫，'
     '政策金額與施行日期會變動，引用前請以原始來源最新公告為準。尚未三讀的草案已註明。'
     % (len(_db['news']), _db['news_checked']), after=8)
for n in _db['news']:
    para(n['date'] + '　' + n['title'], bold=True, after=2)
    para(n['summary'], after=2)
    para('考試連結：' + n['angle'], after=2)
    para('來源：' + n['src'] + '　' + n['url'], after=10)

doc.add_page_break()
h1('資料來源與說明')
bullet('題目與答案：考選部考畢試題查詢平臺，106–115 年專技高考社會工作師，共 115 份考卷')
bullet('測驗題答案以考選部最新公告之更正答案為準；一律給分或多重答案之題目均已標示')
bullet('考試制度、應考資格、及格標準：考選部全球資訊網公告條文')
bullet('116 年考試日程：考選部 116 年專門職業及技術人員考試期日計畫表')
bullet('考點分類為依題幹與選項用詞所作之自動歸類，供聚合複習參考，非官方分類')
bullet('法規類考題可能因法條修正而與現行規定不同，作答與實務應用請以現行條文為準')
para('本指南由題庫資料統計產生，僅供備考參考，不代表考選部立場。', size=12)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print('已產出：', OUT)
print('大小 %.0f KB' % (os.path.getsize(OUT) / 1024))
