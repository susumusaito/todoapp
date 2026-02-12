import json
import os
import urllib.error
import urllib.request

from .models import Todo

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_coach_advice(todos: list[Todo]) -> str:
    api_key = (os.getenv("GROQ_API_KEY") or "").strip()
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
        payload = json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256,
            "temperature": 0.7,
        }).encode("utf-8")

        req = urllib.request.Request(
            GROQ_API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "todoapp/1.0",
            },
        )

        with urllib.request.urlopen(req, timeout=9) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return "⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。"
        return f"⚠️ AI生成エラー: HTTP {e.code}"
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
