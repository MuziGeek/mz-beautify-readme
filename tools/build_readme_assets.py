#!/usr/bin/env python3
"""Build this repository's editable README artwork and localized style specimens."""
from pathlib import Path
from xml.sax.saxutils import escape
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/readme'
STYLES = [
    ('editorial', 'Editorial', '杂志排版', '#f3efe4', '#242b2c', '#c65532'),
    ('terminal', 'Terminal', '终端工具', '#132321', '#e7eee4', '#9bd0a5'),
    ('blueprint', 'Blueprint', '工程蓝图', '#e7edf9', '#253e80', '#4777c4'),
    ('colorblock', 'Colorblock', '色块工作室', '#f2d4c6', '#382d47', '#8851a6'),
    ('minimal', 'Minimal', '黑白极简', '#fafafa', '#181818', '#181818'),
    ('fieldnotes', 'Field notes', '纸上手记', '#f8f2dc', '#343c36', '#c35340'),
]
SANS = 'Segoe UI, Microsoft YaHei, PingFang SC, sans-serif'
SERIF = 'Georgia, SimSun, Songti SC, serif'
MONO = 'Consolas, Menlo, monospace'


class SVG:
    def __init__(self, w, h, title, desc, bg):
        self.w,self.h=w,h
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><desc>{escape(desc)}</desc>']
        self.rect(0,0,w,h,bg)
    def rect(self,x,y,w,h,fill,rx=0,stroke=None):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="2"' if stroke else '')+'/>')
    def text(self,x,y,txt,size=24,fill='#242b2c',weight=400,font=SANS,anchor=None):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}"'+(f' text-anchor="{anchor}"' if anchor else '')+f'>{escape(txt)}</text>')
    def line(self,x1,y1,x2,y2,color,width=2):
        self.parts.append(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{width}" fill="none"/>')
    def path(self,d,color,width=3): self.parts.append(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    def circle(self,x,y,r,color): self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
    def embed(self,child,x,y,scale): self.parts.append(f'<g transform="translate({x} {y}) scale({scale})">'+''.join(child.parts[1:])+'</g>')
    def write(self,path): path.parent.mkdir(parents=True,exist_ok=True); path.write_text('\n'.join(self.parts+['</svg>'])+'\n',encoding='utf-8')


def specimen(style,locale,mobile=False):
    key,en,zh,bg,ink,accent=style
    cn=locale=='zh-CN'; w,h=(360,320) if mobile else (1200,620)
    s=SVG(w,h,'MZ Beautify README — '+(zh if cn else en),'风格构图示例；不是实际应用界面。' if cn else 'A composition specimen, not a screenshot of an application.',bg)
    steps=['读项目','做设计','看成品'] if cn else ['Read','Design','Review']
    promise='以真实内容，设计项目首页。' if cn else 'Design the page around real proof.'
    if key=='editorial':
        s.text(22 if mobile else 60,32 if mobile else 65,'MZ / BEAUTIFY',13 if mobile else 23,ink,600)
        s.line(22 if mobile else 60,46 if mobile else 90,w-22 if mobile else w-60,46 if mobile else 90,ink,1)
        s.text(17 if mobile else 47,155 if mobile else 296,'README',68 if mobile else 206,ink,400,SERIF)
        s.rect(24 if mobile else 62,185 if mobile else 352,40 if mobile else 83,5 if mobile else 9,accent)
        s.text(24 if mobile else 62,222 if mobile else 426,promise,18 if mobile else 39,ink,400,SERIF if not cn else SANS)
        for i,step in enumerate(steps): s.text(24+i*108 if mobile else 62+i*355,286 if mobile else 550,f'0{i+1}  {step}',14 if mobile else 26,accent,600)
    elif key=='terminal':
        for i,color in enumerate(['#d47f6b','#dcc47b','#9bd0a5']):s.circle(26+i*19 if mobile else 64+i*31,29 if mobile else 57,4 if mobile else 7,color)
        s.text(22 if mobile else 59,78 if mobile else 130,'MZ / BEAUTIFY',13 if mobile else 23,'#a5baae',500,MONO)
        s.text(19 if mobile else 50,155 if mobile else 293,'README',68 if mobile else 197,ink,700,MONO)
        s.rect(281 if mobile else 813,108 if mobile else 157,24 if mobile else 63,51 if mobile else 142,accent)
        s.text(23 if mobile else 60,203 if mobile else 383,promise,17 if mobile else 35,ink)
        for i,step in enumerate(steps):s.text(25 if mobile else 63,243+i*25 if mobile else 457+i*50,f'{i+1:02d} / {step}',15 if mobile else 30,accent,500,MONO if not cn else SANS)
    elif key=='blueprint':
        gap=24 if mobile else 60
        for x in range(0,w,gap):s.line(x,0,x,h,'#cfdbef',1)
        for y in range(0,h,gap):s.line(0,y,w,y,'#cfdbef',1)
        s.text(22 if mobile else 60,38 if mobile else 65,'MZ / BEAUTIFY',13 if mobile else 23,ink,600,MONO)
        s.text(20 if mobile else 53,125 if mobile else 241,'README',65 if mobile else 175,ink,600)
        s.text(23 if mobile else 60,169 if mobile else 314,promise,17 if mobile else 36,ink)
        for i,step in enumerate(steps):
            x=23+i*111 if mobile else 60+i*375
            s.rect(x,207 if mobile else 392,93 if mobile else 310,70 if mobile else 138,bg,0,accent)
            s.text(x+11 if mobile else x+25,232 if mobile else 438,f'0{i+1}',12 if mobile else 22,accent,600,MONO)
            s.text(x+11 if mobile else x+25,259 if mobile else 494,step,16 if mobile else 35,ink,600)
            if i<2:s.line(x+(93 if mobile else 310),243 if mobile else 461,x+(111 if mobile else 375),243 if mobile else 461,accent,3)
    elif key=='colorblock':
        s.rect(0,0,w*.34,h,'#eed37e')
        s.rect(w*.67,0,w*.33,h*.5,'#c8b5df')
        s.rect(w*.34,h*.67,w*.66,h*.33,'#df775a')
        s.circle(w*.82,h*.22,45 if mobile else 100,'#8851a6')
        s.text(22 if mobile else 57,36 if mobile else 66,'MZ / BEAUTIFY',13 if mobile else 23,ink,700)
        s.text(17 if mobile else 46,140 if mobile else 280,'README',68 if mobile else 197,ink,800)
        s.text(22 if mobile else 59,183 if mobile else 368,promise,17 if mobile else 37,ink,500)
        for i,step in enumerate(steps):s.text(23+i*111 if mobile else 60+i*375,280 if mobile else 549,step,16 if mobile else 35,ink,600)
    elif key=='minimal':
        s.text(w/2,40 if mobile else 72,'MZ / BEAUTIFY',13 if mobile else 25,ink,500,anchor='middle')
        s.text(w/2,152 if mobile else 291,'README',67 if mobile else 191,ink,750,anchor='middle')
        s.text(w/2,196 if mobile else 382,promise,17 if mobile else 35,ink,400,anchor='middle')
        s.line(140 if mobile else 480,230 if mobile else 455,220 if mobile else 720,230 if mobile else 455,ink,2)
        s.text(w/2,278 if mobile else 548,' / '.join(steps),15 if mobile else 30,ink,500,anchor='middle')
    elif key=='fieldnotes':
        for y in range(58 if mobile else 92,h,28 if mobile else 55):s.line(0,y,w,y,'#dedcca',1)
        s.line(45 if mobile else 124,0,45 if mobile else 124,h,'#d68877',2)
        s.text(63 if mobile else 168,39 if mobile else 64,'MZ / BEAUTIFY',13 if mobile else 23,ink,600)
        s.text(60 if mobile else 160,132 if mobile else 264,'README',57 if mobile else 177,ink,400,SERIF)
        s.path('M61 150Q178 135 329 149' if mobile else 'M164 302Q581 267 1090 304',accent,3 if mobile else 6)
        s.text(63 if mobile else 171,190 if mobile else 386,'真实内容，清楚呈现。' if cn else 'Real proof. Clear pages.',19 if mobile else 40,ink,400,SERIF if not cn else SANS)
        for i,step in enumerate(steps):
            x=64+i*95 if mobile else 173+i*310
            s.text(x,266 if mobile else 523,step,15 if mobile else 32,ink,600)
        s.path('M278 209l10 9 18-22' if mobile else 'M990 419l29 25 46-61',accent,3 if mobile else 7)
    return s


def hero(locale,mobile=False):
    cn=locale=='zh-CN';w,h=(360,520) if mobile else (1200,520)
    s=SVG(w,h,'MZ Beautify README','从项目事实到可评审的 README：文案、视觉、多语言预览。' if cn else 'From repository facts to a reviewable README: copy, visuals and localized previews.','#f2eee4')
    s.text(24 if mobile else 52,37 if mobile else 55,'MZ / BEAUTIFY README',14 if mobile else 24,'#343b3b',650)
    s.line(24 if mobile else 52,54 if mobile else 78,w-24 if mobile else w-52,54 if mobile else 78,'#c9c7bb',1)
    if mobile:
        lines=['让项目，','一眼读懂。'] if cn else ['Your README,','clearly told.']
        for i,line in enumerate(lines):s.text(21,126+i*60,line,50 if cn else 40,'#242b2c',500,SANS if cn else SERIF)
        s.text(24,229,'内容 · 视觉 · 多语言预览' if cn else 'Copy. Visuals. Localized previews.',17,'#5d655e')
        s.embed(specimen(STYLES[1],locale,True),24,262,.44)
        s.embed(specimen(STYLES[2],locale,True),178,302,.44)
        s.rect(24,472,38,4,'#c65532')
        s.text(76,480,'源于项目，交付前验证。' if cn else 'From source. Checked in context.',13,'#434c47',550)
    else:
        lines=['让项目，','一眼读懂。'] if cn else ['Your README,','clearly told.']
        for i,line in enumerate(lines):s.text(49,203+i*111,line,96 if cn else 91,'#242b2c',500,SANS if cn else SERIF)
        s.text(54,381,'内容 · 视觉 · 多语言预览' if cn else 'Copy. Visuals. Localized previews.',30,'#5d655e')
        s.embed(specimen(STYLES[1],locale),752,120,.3)
        s.embed(specimen(STYLES[2],locale),695,286,.32)
        s.rect(54,451,60,5,'#c65532');s.text(136,463,'源于项目，交付前验证。' if cn else 'From source. Checked in context.',23,'#434c47',550)
    return s


def gallery(locale,mobile=False):
    cn=locale=='zh-CN'; w,h=(360,2040) if mobile else (1200,610)
    s=SVG(w,h,'六种 README 设计方向' if cn else 'Six README design directions','本仓库的 SVG 构图示例；每种风格都有独立的手机布局。' if cn else 'SVG composition specimens with separate mobile layouts.','#ffffff')
    for i,style in enumerate(STYLES):
        if mobile:
            y=i*340;s.embed(specimen(style,locale,True),16,y,.91)
            s.text(18,y+316,f'0{i+1} / '+(style[2] if cn else style[1]),19,'#242b2c',650)
        else:
            x=(i%3)*400+12;y=(i//3)*305
            s.embed(specimen(style,locale),x,y,376/1200)
            s.text(x+8,y+238,f'0{i+1}',21,'#727b77',550,MONO)
            s.text(x+65,y+240,style[2] if cn else style[1],29,'#242b2c',650)
            # A paper frame separates the actual rendered designs without simulating a product UI.
    return s


def build():
    for locale in ('en','zh-CN'):
        suffix='' if locale=='en' else '.zh-CN'
        for mobile in (False,True):
            size='.mobile' if mobile else ''
            hero(locale,mobile).write(OUT/f'hero{suffix}{size}.svg')
            gallery(locale,mobile).write(OUT/f'styles{suffix}{size}.svg')
            for style in STYLES:specimen(style,locale,mobile).write(OUT/'styles'/f'{style[0]}{suffix}{size}.svg')
    index={'format':'mz.readme-style-examples/1','note':'Generated composition examples, not installed Engine presets.',
           'styles':[{'id':s[0],'en':s[1],'zh-CN':s[2],'implementation':'svg','locales':['en','zh-CN'],'viewports':['desktop','mobile']} for s in STYLES]}
    (OUT/'styles/index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Built 32 localized, responsive SVG assets.')


if __name__=='__main__':build()
