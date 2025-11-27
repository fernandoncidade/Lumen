import asyncio
import json
import sys
from pathlib import Path

def list_pyttsx3():
    try:
        import pyttsx3

    except Exception as e:
        return {"error": f"pyttsx3 import failed: {e}"}

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices") or []
        out = []
        for v in voices:
            item = {
                "id": getattr(v, "id", None),
                "name": getattr(v, "name", None),
                "languages": getattr(v, "languages", None),
                "gender": getattr(v, "gender", None),
                "age": getattr(v, "age", None)
            }

            out.append(item)

        try:
            engine.stop()

        except Exception:
            pass

        return {"voices": out}

    except Exception as e:
        return {"error": f"pyttsx3 listing failed: {e}"}

async def try_edge_async(func):
    try:
        res = await func()
        return res

    except Exception as e:
        return {"_edge_error": str(e)}

def list_edge_tts():
    try:
        import edge_tts

    except Exception as e:
        return {"error": f"edge_tts import failed: {e}"}

    candidates = []
    if hasattr(edge_tts, "list_voices"):
        candidates.append(("list_voices", edge_tts.list_voices))

    if hasattr(edge_tts, "voices"):
        candidates.append(("voices", edge_tts.voices))

    if hasattr(edge_tts, "Voices") or hasattr(edge_tts, "Voice"):
        candidates.append(("attr_Voices/Voice", lambda: getattr(edge_tts, "Voices", getattr(edge_tts, "Voice"))))

    results = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for name, fn in candidates:
        try:
            if asyncio.iscoroutinefunction(fn):
                res = loop.run_until_complete(try_edge_async(fn))

            else:
                try:
                    res = fn()

                except TypeError:
                    res = loop.run_until_complete(try_edge_async(fn))

            results[name] = res

        except Exception as e:
            results[name] = {"error": str(e)}

    formatted = {}
    for k, v in results.items():
        try:
            if isinstance(v, list):
                out = []
                for it in v:
                    if isinstance(it, dict):
                        out.append({
                            "id": it.get("Name") or it.get("ShortName") or it.get("voiceName") or it.get("Id") or it.get("id"),
                            "name": it.get("DisplayName") or it.get("Name") or it.get("Voice") or it.get("ShortName"),
                            "locale": it.get("Locale") or it.get("LocaleName") or it.get("Locale"),
                            "raw": it
                        })

                    else:
                        out.append({"repr": repr(it)})

                formatted[k] = out

            else:
                formatted[k] = v

        except Exception:
            formatted[k] = {"raw": repr(v)}

    try:
        loop.close()

    except Exception:
        pass

    return formatted

def _format_human_readable(out_dict):
    lines = []
    lines.append("Voices listing\n")
    py = out_dict.get("pyttsx3")
    lines.append("=== pyttsx3 ===")

    if not py:
        lines.append("  (no data)")

    else:
        if "error" in py:
            lines.append(f"  Error: {py['error']}")

        else:
            voices = py.get("voices") or []
            if not voices:
                lines.append("  (no voices found)")

            else:
                for i, v in enumerate(voices, 1):
                    lines.append(f"  [{i}] id: {v.get('id')} name: {v.get('name')}")
                    lines.append(f"       languages: {v.get('languages')} gender: {v.get('gender')} age: {v.get('age')}")

    lines.append("")

    ed = out_dict.get("edge_tts")
    lines.append("=== edge_tts ===")

    if not ed:
        lines.append("  (no data)")

    else:
        if isinstance(ed, dict) and "error" in ed:
            lines.append(f"  Error: {ed['error']}")

        else:
            for key, val in (ed.items() if isinstance(ed, dict) else []):
                lines.append(f"-- source: {key} --")
                if isinstance(val, list):
                    if not val:
                        lines.append("  (no voices)")

                    else:
                        for i, v in enumerate(val, 1):
                            if isinstance(v, dict):
                                lines.append(f"  [{i}] id: {v.get('id')} name: {v.get('name')} locale: {v.get('locale')}")

                            else:
                                lines.append(f"  [{i}] {repr(v)}")

                else:
                    lines.append(f"  {repr(val)}")

    return "\n".join(lines)

def main():
    out = {
        "pyttsx3": list_pyttsx3(),
        "edge_tts": list_edge_tts()
    }

    print(json.dumps(out, ensure_ascii=False, indent=2))

    try:
        try:
            script_path = Path(__file__).resolve()

        except NameError:
            if sys.argv and sys.argv[0]:
                script_path = Path(sys.argv[0]).resolve()

            else:
                script_path = Path.cwd()

        if not script_path.exists() and hasattr(sys, "_MEIPASS"):
            script_path = Path(sys._MEIPASS)

        script_dir = script_path.parent if script_path.is_file() else script_path

        txt_path = script_dir / "voices_list.txt"
        json_path = script_dir / "voices_list.json"

        human = _format_human_readable(out)

        txt_path.write_text(human, encoding="utf-8")
        json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\nArquivo gerado: {txt_path}")
        print(f"JSON gerado: {json_path}")

    except Exception as e:
        print(f"Falha ao salvar arquivos: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
