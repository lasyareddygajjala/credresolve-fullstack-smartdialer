Agent: OFFLINE → AVAILABLE → RESERVED → DIALING → CONNECTED → WRAP_UP → AVAILABLE. AVAILABLE can become PAUSED or OFFLINE.
Call: QUEUED → RESERVED → INITIATED → RINGING → ANSWERED → CONNECTED → COMPLETED. Pre-connect states may fail/cancel.
The implementation rejects illegal state regressions and repeated event IDs.
