# Clinical Rotation Assignment System Diagrams

## 1. System Flowchart (Overall Flow)

```mermaid
flowchart TD
    classDef entity fill:#ffffff,stroke:#ffb6c1,stroke-width:2px,color:#333333;
    classDef process fill:#fff0f5,stroke:#ff69b4,stroke-width:2px,color:#333333;
    classDef decision fill:#ffffff,stroke:#ff69b4,stroke-width:2px,shape:diamond,color:#333333;
    classDef startend fill:#ffb6c1,stroke:#ff1493,stroke-width:2px,color:#ffffff;

    Start([Start]):::startend
    A_Log(Admin Login):::process
    S_Log(Student Login):::process
    
    ManageStu(Input / Manage Student Records):::process
    CreateSched(Create Rotation Schedule):::process
    AssignArea(Assign Students to Clinical Areas):::process
    CheckConflict{Conflicts\nFound?}:::decision
    Adjust(Adjust Schedule):::process
    SaveSched(Save Final Schedule):::process
    
    ViewSched(View Assigned Area & Schedule):::process
    RecAnnounce(Receive Announcements):::process
    End([End]):::startend

    Start --> Space1:::entity
    Start --> A_Log
    Start --> S_Log
    
    A_Log --> ManageStu
    ManageStu --> CreateSched
    CreateSched --> AssignArea
    AssignArea --> CheckConflict
    
    CheckConflict -- Yes --> Adjust
    Adjust --> CheckConflict
    CheckConflict -- No --> SaveSched
    
    S_Log --> ViewSched
    SaveSched -. Automated Notification .-> ViewSched
    ViewSched --> RecAnnounce
    
    SaveSched --> End
    RecAnnounce --> End
    
    linkStyle default stroke:#ff69b4,stroke-width:2px;
```

**Description:**
This flowchart illustrates the end-to-end journey within the system, split between the **Admin** and **Student** flows. 
- **The Admin Flow** handles data ingestion (creating student records and base schedules) followed by the critical assignment process. A decision node (`Conflicts Found?`) enforces system validation: if a schedule overlaps or violates capacity, the admin is forced to adapt the schedule (`Adjust Schedule`) until the system clears it (`No Conflicts`).
- **The Student Flow** runs parallel, where students log in to view their approved areas and schedules. A connection is mapped showing that once the admin saves the final schedule, the student interface is updated.


---

## 2. DFD Level 0 (Context & Main Processes)

```mermaid
flowchart TD
    classDef entity fill:#ffffff,stroke:#ffb6c1,stroke-width:2px,color:#333333;
    classDef process fill:#fff0f5,stroke:#ff69b4,stroke-width:2px,color:#333333;
    classDef datastore fill:#ffffff,stroke:#ffb6c1,stroke-width:2px,color:#333333;

    %% Entities
    Admin[Admin]:::entity
    Student[Student]:::entity

    %% Processes
    P1((1.0 Manage\nStudent Records)):::process
    P2((2.0 Manage\nRotation Schedule)):::process
    P3((3.0 Assign Clinical\nAreas & Validate)):::process
    P4((4.0 Provide\nStudent Access)):::process

    %% Data Stores
    D1[(D1: Student\nDatabase)]:::datastore
    D2[(D2: Rotation\nSchedule Database)]:::datastore

    %% Flows
    Admin -- Student Info --> P1
    Admin -- Schedule Parameters --> P2
    Admin -- Assignment Details --> P3

    P1 -- New/Update Info --> D1
    P2 -- Formatted Schedules --> D2
    
    D1 -- Student Data --> P3
    D2 -- Available Slots --> P3
    P3 -- Validated Assignment --> D2
    P3 -- Conflict Alerts --> Admin

    Student -- Login/Request --> P4
    D1 -. Retrieve Student Info .-> P4
    D2 -. Retrieve Assigned Schedule .-> P4
    P4 -- Display Schedule & Info --> Student
    
    linkStyle default stroke:#ff69b4,stroke-width:2px;
```

**Description:**
The DFD Level 0 maps out the core high-level modules of the system and how data moves between external entities (Admin and Student), processes, and data stores (Databases).
- **Process 1.0 & 2.0** represent fundamental CRUD (Create, Read, Update, Delete) operations feeding `D1` and `D2`.
- **Process 3.0** is the brain of the system, consuming data from both databases to map students to clinical rotation areas while providing feedback loops regarding conflicts straight to the Admin.
- **Process 4.0** acts as the delivery mechanism, pulling validated data from the databases and rendering it nicely to the Student entity interface.

---

## 3. DFD Level 1 (Decomposition of Process 3 - Assignment)

```mermaid
flowchart TD
    classDef entity fill:#ffffff,stroke:#ffb6c1,stroke-width:2px,color:#333333;
    classDef process fill:#fff0f5,stroke:#ff69b4,stroke-width:2px,color:#333333;
    classDef datastore fill:#ffffff,stroke:#ffb6c1,stroke-width:2px,color:#333333;

    Admin[Admin]:::entity
    D1[(D1: Student\nDatabase)]:::datastore
    D2[(D2: Rotation\nSchedule Database)]:::datastore

    P31((3.1 Fetch\nStudent Data)):::process
    P32((3.2 Fetch Area\nAvailability)):::process
    P33((3.3 Process Tentative\nAssignment)):::process
    P34((3.4 Check Conflicts\n& Validate)):::process
    P35((3.5 Update Final\nSchedule)):::process
    
    Admin -- Select Student vs Area --> P33
    
    D1 -- Profile & History --> P31
    D2 -- Current Usage/Limits --> P32
    
    P31 -- Formatted Student Info --> P33
    P32 -- Valid Slot Data --> P33
    
    P33 -- Tentative Assignment --> P34
    
    P34 -- Conflict Detected Alert --> Admin
    P34 -- Validation Success --> P35
    
    P35 -- Finalized Assignment --> D2
    P35 -- Confirmation Message --> Admin

    linkStyle default stroke:#ff69b4,stroke-width:2px;
```

**Description:**
This internal diagram breaks down exactly how Process 3.0 assigns students and checks for conflicts.
- **Sub-processes 3.1 & 3.2** handle data retrieval, guaranteeing we are evaluating the assignment with up-to-date data.
- **Sub-process 3.3** bridges the Admin's command with the system data to create a *Tentative Assignment*.
- **Sub-process 3.4** is the validation gateway. It strictly denies overlapping schedules and alerts the Admin to make changes. Only if the validation logic is successful, does it hand the record forward.
- **Sub-process 3.5** locks it in, pushing the result to the main `Rotation Schedule Database` securely.
