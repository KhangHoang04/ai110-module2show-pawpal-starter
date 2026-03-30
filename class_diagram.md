# PawPal+ Class Diagram (Mermaid.js)

Paste the code block below into the [Mermaid Live Editor](https://mermaid.live) or preview it in VS Code with a Mermaid extension.

```mermaid
classDiagram
    class Pet {
        +String name
        +String species
        +int age
        +List~String~ special_needs
        +summary() String
    }

    class Owner {
        +String name
        +List~Pet~ pets
        +int available_minutes
        +add_pet(pet: Pet) None
        +remove_pet(pet_name: String) None
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String pet_name
        +bool completed
        +mark_complete() None
        +priority_value() int
    }

    class Scheduler {
        +Owner owner
        +List~Task~ tasks
        +generate_schedule() List~Task~
        +explain_plan(schedule: List~Task~) String
    }

    Owner "1" --> "*" Pet : has
    Task "*" --> "1" Pet : associated with
    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "*" Task : schedules
```
