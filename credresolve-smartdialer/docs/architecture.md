```mermaid
flowchart LR
Campaign --> Pacing[Progressive / Predictive]
Pacing --> Safety[Safety Controller]
Safety --> Allocator[Atomic Agent + Borrower Reservation]
Allocator --> Adapter[Provider Adapter]
Adapter --> A[Mock Provider A]
Adapter --> B[Mock Provider B]
A --> Events[Idempotent Event Processor]
B --> Events
```
