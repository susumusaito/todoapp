import os

from .models import Todo


def generate_coach_advice(todos: list[Todo]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        return "⚠️ GROQ_API_KEY が設定されていません。.env ファイルを確認してください。"

    if not todos:
        return "タスクがまだありません。まずはタスクを追加してみましょう！"

    task_summary = _build_task_summary(todos[:10])
    prompt = (
        f"タスク管理コーチとして以下を分析し、日本語で短いアドバイスを3つ書いて。\n"
        f"{task_summary}"
    )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.7,
        )
        return response.choices[0].message.content
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
