"""Two-chat meeting companion for macOS. Run with Python 3.8 or later."""
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request


class Meeting:
    def __init__(self):
        self.active = "A"
        self.histories = {"A": [], "B": []}
        self.minutes = []
        self.tasks = []
        self.dots = []
        self.voice = False
        self.speaker = None

    def silence(self):
        if self.speaker and self.speaker.poll() is None:
            self.speaker.terminate()
            self.speaker.wait()
        self.speaker = None

    def speak(self, text):
        self.silence()
        if self.voice:
            self.speaker = subprocess.Popen(["say", text], stdin=subprocess.DEVNULL)

    def round(self, prompt, reply, shared):
        actors = [self.active]
        if shared:
            actors.append("B" if self.active == "A" else "A")
            self.minutes.append(("You", prompt))
        for actor in actors:
            history = self.minutes if shared else self.histories[actor]
            context = history if shared else history + [("You", prompt)]
            answer = reply(actor, context)
            if not answer.strip():
                raise ValueError("Empty reply. The turn was left open.")
            if not shared:
                history.append(("You", prompt))
            history.append((actor, answer))
            print(f"Chat {actor}> {answer}")
            if shared:
                source = len(history)
                for line in answer.splitlines():
                    for marker, records in [("HANDOFF ", self.tasks), ("DOT ", self.dots)]:
                        if line.startswith(marker) and line[len(marker):].strip():
                            other = "B" if actor == "A" else "A"
                            records.append((source, actor, other, line[len(marker):].strip()))
        self.speak(history[-1][1])


def reply(actor, history):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return input(f"Paste Chat {actor}'s reply (manual relay)> ")
    role = "planner" if actor == "A" else "reviewer"
    instruction = (
        f"You are Chat {actor}, the {role}. Respond to the latest turn in context. "
        "During a meeting, delegate a concrete task to the other chat with a line starting "
        "HANDOFF followed by the task. Mark a durable connection or decision with a line "
        "starting DOT followed by the note. Treat handoffs as requests."
    )
    payload = dict(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), store=False,
                   instructions=instruction, input=json.dumps(history, ensure_ascii=False))
    request = urllib.request.Request("https://api.openai.com/v1/responses",
                                     data=json.dumps(payload).encode(),
                                     headers={"Authorization": "Bearer " + key,
                                              "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    return "\n".join(part["text"] for item in result.get("output", [])
                     for part in item.get("content", []) if part.get("type") == "output_text")


HELP = """/a or /b switches the active chat and ends spoken playback.
/voice enables Mac spoken replies. /endvoice stops playback immediately.
/meet TOPIC gives each chat one turn in the shared meeting.
/minutes shows the shared transcript. /board shows tasks and dots.
/facetime ADDRESS opens a FaceTime invitation on your Mac. /quit exits.
Type any other message for a private turn with the selected chat."""


def main():
    session = Meeting()
    print(HELP)
    try:
        while True:
            line = input(f"[Chat {session.active}] ").strip()
            cmd, _, arg = line.partition(" ")
            try:
                if cmd == "/quit":
                    break
                if cmd in ("/a", "/b", "/endvoice"):
                    session.silence()
                    session.voice = False
                    if cmd != "/endvoice":
                        session.active = cmd[-1].upper()
                elif cmd == "/voice":
                    session.voice = bool(shutil.which("say"))
                    print("Spoken replies on." if session.voice else "Mac speech unavailable.")
                elif cmd == "/meet" and arg:
                    session.round(arg, reply, shared=True)
                elif cmd == "/facetime" and arg and shutil.which("say"):
                    subprocess.run(["open", "facetime://" + urllib.parse.quote(arg, safe="@+")], check=True)
                elif cmd == "/minutes":
                    for i, (who, message) in enumerate(session.minutes, 1):
                        print(f"{i}. {who}> {message}")
                elif cmd == "/board":
                    for label, records in [("Task", session.tasks), ("Dot", session.dots)]:
                        for source, author, recipient, note in records:
                            owner = f" → {recipient}" if label == "Task" else ""
                            print(f"{label} · minute {source} · {author}{owner} · {note}")
                elif cmd.startswith("/"):
                    print(HELP)
                elif line:
                    session.round(line, reply, shared=False)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                print(f"Turn stopped: {error}")
    except (EOFError, KeyboardInterrupt):
        print()
    finally:
        session.silence()


if __name__ == "__main__":
    main()
