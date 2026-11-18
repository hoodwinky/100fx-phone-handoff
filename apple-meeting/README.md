# Two chats at one table

A Mac companion prototype for the FreeX FaceTime handoff proposal. You chair the meeting. Chat A plans, Chat B reviews, and each can delegate to the other. A dot records an idea or decision and points back to the meeting turn that produced it.

## Try it on Mac

With Python 3.8 or later installed, run `python3 apple-meeting/meeting.py` from the repository root. With no credentials, paste replies from two chats yourself. For automatic replies, set OPENAI_API_KEY in your shell before launch. OPENAI_MODEL can override the default model. API mode uses separate, billable model conversations. Only the current private thread or the shared minutes are sent for a turn. Keep the terminal open to retain the session.

1. Type a private question in A. Switch with `/b` and ask B a different question. Switching stops spoken playback. To use Apple Dictation, place the cursor at the prompt and start Dictation using your configured shortcut.
2. Use `/voice` for spoken replies. Use `/endvoice` to stop playback and continue typing. In a meeting, playback reads the last reply. Dictation and ChatGPT Voice each have their own stop controls.
3. Enter `/meet What should we decide before inviting a guest?`. The selected chat speaks first. The other receives that reply and responds. Enter another meeting prompt to continue. Each meeting round uses only shared minutes. To bring in private context, include the chosen excerpt in your meeting prompt.
4. In manual mode try entering `HANDOFF Check the guest’s availability` as the first reply and `DOT Recording depends on guest availability` as the second. Use `/board` to see the task owner and source for each entry. Use `/minutes` for the numbered transcript. Handoffs are assignments recorded for discussion.
5. Use `/facetime name@example.com` with your intended participant’s actual Apple contact. Complete the call in FaceTime. You can discuss the meeting and read selected minutes aloud. Keep private threads off any shared screen. End the human call in FaceTime.

## Native integration proposal

On iPhone and Mac, the intended interaction is **End Voice → Switch Chat → Invite Both to Meeting**. Each thread retains its history. Before joining, the person chooses what either chat can contribute. Both chats are identified as AI, and each handoff or dot links to its source turn. Ending the meeting stops turn-taking.

The prototype launches a human FaceTime call and runs the two chat roles alongside it. Native ChatGPT thread selection, AI caller tiles, live FaceTime audio and SharePlay synchronisation remain proposed. For a native Apple client, a GroupActivity could share the meeting board with participants. A GroupSessionMessenger could transmit approved meeting events and a snapshot for late joiners. Private chats would stay outside the group session. An Apple-device test should verify joining, leaving, reconnection, microphone ownership and VoiceOver before pursuing live audio.

[Apple Group Activities](https://developer.apple.com/documentation/GroupActivities) · [ChatGPT Voice](https://help.openai.com/en/articles/20001274-chatgpt-voice)
