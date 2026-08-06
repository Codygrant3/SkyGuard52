# Mission 1 Acceptance Matrix Addendum — Recovery04 Binding01 Terminal

| Gate | Result | Evidence |
|---|---|---|
| Recovery04 runtime-binding freeze | Passed | SHA-256 `f68b263354e9b4663d1bb28e518ba38343f0aad35005e8ab2722fe92c07f2a24` |
| Frozen execution preflight | Passed | `Saved/Reports/PHASE4_M01_RECOVERY04_BINDING01_EXECUTION_PREFLIGHT.json` |
| Accepted DLL parity | Passed | SHA-256 `2070765a5d44199f7116c2038c97d866b91a509706de73953ead1cad057cb6e3` |
| Unreal launch count | Passed | Exactly `1` |
| Automatic retry exclusion | Passed | Retry count `0` |
| Supervisor terminal evidence | Passed | Numeric `System.Int32` exit code `-1`; timeout `true` |
| Governed runtime namespace | Failed | Never created |
| Native lifecycle heartbeat | Failed | Not produced |
| Shader readiness and warmup | Failed | No governed evidence |
| 30-second measurement / 900 samples | Failed | No frame samples |
| Five static and three temporal PNGs | Failed | `0/8` produced |
| Capture receipt | Failed | Not produced |
| Material restoration receipt | Failed | Not produced |
| Native terminal receipt | Failed | Not produced |
| Human visual inspection | Not possible | No governed PNGs |
| Network-isolated execution | Failed | TcpMessaging and UdpMessaging initialized; UDP bound and joined multicast |
| Unique runtime module binding | Failed | Recovery04 module already associated with Recovery01 |
| Environment assembly integrity | Failed | Ocean, beach, and land tile attachments aborted |
| Representative visual acceptance | Failed | `FAILED_WITH_EVIDENCE` |
| Performance and temporal stability acceptance | Not evaluated | Required samples absent |
| Promotion, integration, or packaging | Not authorized | None performed |

Mission 1 remains unaccepted for production visuals.

Next executable gate: `Offline-only Recovery05 runtime startup and isolation correction design`.
