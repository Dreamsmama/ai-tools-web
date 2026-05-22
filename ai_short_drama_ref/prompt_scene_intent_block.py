"""职业观察局：sceneIntent、sceneDescription 与场景标注说明（供 LLM Prompt 复用）。"""

from app.ai_short_drama.life_moment_visual import prompt_life_moment_block
from app.ai_short_drama.visual_director import VISUAL_DIRECTOR_SYSTEM

SCENE_INTENT_PROMPT_BLOCK = """
6. sceneIntent（必须按本段文案语义变化，禁止全片相同）:
   opening | communication | work_pressure | fatigue | collapse | emotion | daily_life
7. sceneDescription（中文 40-90 字，电影镜头式画面，不是职业介绍）:
   - 写「真实互联网人的某个瞬间」，禁止「XX在办公室做YY」
   - 每段至少 2 项生活碎片：冷咖啡、地铁、雨夜、便利店、凌晨办公室、手机消息、城市夜景等
   - 职业符号可轻量出现（虚化/一角），勿让软件界面占满画面
   - 竖屏9:16，上下字幕留白
8. scene 优先夜景/生活场景键：night_office | office_night | office_day（少写 desk/meeting_room）
9. imageTags：sceneIntent + emotion + life tag（cold_coffee/subway_night/rainy_window）+ 少量职业 tag
10. 配图 = 文案语义 + sceneIntent + 生活碎片 + 情绪；职业只是点缀
""" + prompt_life_moment_block()

SCENE_INTENT_EXAMPLE_SEGMENT = """
    {{
      "segmentNo": 1,
      "text": "很多人觉得：",
      "role": "{example_role}",
      "emotion": "calm",
      "sceneIntent": "opening",
      "scene": "office_night",
      "sceneDescription": "清晨地铁车厢窗边，城市晨光虚化，通勤背影，耳机，无人正脸，生活感留白，竖屏冷色调",
      "imageTags": ["opening", "subway_night", "commute", "calm", "life_moment"]
    }},
    {{
      "segmentNo": 2,
      "text": "老板会说：为什么还没上线？",
      "role": "{example_role}",
      "emotion": "stressed",
      "sceneIntent": "work_pressure",
      "scene": "night_office",
      "sceneDescription": "凌晨办公室，冷掉的咖啡，手机飞书红点，窗外城市夜景，显示器微光，压迫疲惫，非人物正脸",
      "imageTags": ["work_pressure", "cold_coffee", "phone_message", "city_night", "stressed"]
    }}
"""

VISUAL_DIRECTOR_PROMPT_APPENDIX = (
    "\n\n"
    + VISUAL_DIRECTOR_SYSTEM
    + "\n\n拆段时为每段撰写 sceneDescription（生活情绪切片，供 AI 配图）。"
)
