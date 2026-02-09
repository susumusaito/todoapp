import os

from .models import Todo


def generate_coach_advice(todos: list[Todo]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    if not api_key:
        return "⚠️ GEMINI_API_KEY が設定されていません。.env ファイルを確認してください。"

    if not todos:
        return "タスクがまだありません。まずはタスクを追加してみましょう！"

    task_summary = _build_task_summary(todos)
    prompt = f"""あなたは優秀なタスク管理コーチです。以下のタスク状況を分析して、
日本語で簡潔なアドバイスを3つ以内で提供してください。
優先度、期限、進捗を考慮して具体的な行動提案をしてください。

【タスク状況】
{task_summary}

アドバイス:"""

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI生成エラー: {e}"


def _build_task_summary(todos: list[Todo]) -> str:
    lines = []
    for t in todos:
        due = t.due_date.strftime("%Y-%m-%d") if t.due_date else "期限なし"
        lines.append(
            f"- {t.title} | 状態:{t.status} | 優先度:{t.priority} | "
            f"期限:{due} | 進捗:{t.progress}%"
        )
    return "\n".join(lines)
