# Stream Integration
This is my Python codebase for creating interactive features in my streams.

Components:

 - TwitchAPI: [Documentation](https://pytwitchapi.dev/en/stable/)
 - DECTalk: Uses serial

## Code Design

This code uses a emitter/receiver signal concept to connect different sources together. There are three signal types currently used:

 - `chat` (Name, Color, Message Text, Donate Amount): Exchanges all messages sent in standard chat.
 - `interact` (Name, Interact-Type, Message Text): For anything outside of normal chat messages that needs to be responded to.
 - `donate` (Name, Donate Value/Type, Message Text): All donations that can be from inside chat or other sources.

This allows me to decouple the logic of the different components. Receivers are
registered to emitters and when a new signal is ready it is sent to all receivers.

For example, here the `Twitch API` emitter can have receivers for multiple outputs:

 - `Twitch API`
 - - `DECTalk`
 - - `CLI Print`

Another emitter object could be added and connect all the receivers to it with
only a couple lines of code.

