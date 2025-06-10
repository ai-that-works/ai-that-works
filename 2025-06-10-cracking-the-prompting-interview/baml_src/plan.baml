class EventPreparationPlan {
  preEventTasks string[] @description("Tasks to complete before the event")
  networkingTargets NetworkingTarget[] @description("Companies and people to prioritize connecting with")
  projectIdeas string[] @description("Potential project ideas for the hackathon")
  presentationStrategy string @description("Strategy for demo presentation if participating")
  timeManagementPlan string @description("How to best utilize the time during different segments of the event")
}

class NetworkingTarget {
    name Entity
    reason string
    value "high" | "medium" | "low" @description(#"
        how valuable the person/entity is to myself and my career goals
    "#)
}

class Company {
    type "company"
    name string
}

class Person {
    type "person"
    first_name string?
    last_name string?
    
    @@assert({{ first_name || last_name }})
}

type Entity = Company | Person

function GenerateHackNightPlan(eventDescription: string) -> EventPreparationPlan {
  client "anthropic/claude-3-5-haiku-latest"
  prompt #"
    You are an experienced tech event strategist. Create a strategic plan for making the most of this hackathon/networking event.
    Focus on practical, actionable items that will help maximize value from the event.

    {{ ctx.output_format }}

    {{ _.role("user") }} {{ eventDescription }}
  "#
}

test BasicEventPlan {
  functions [GenerateHackNightPlan]
  args {
    eventDescription #"
      Join us for a Tech Meetup!
      Schedule:
      6:00 PM: Networking
      7:00 PM: Presentations
      8:00 PM: Open Hacking
    "#
  }
}

test GitHubHackNight {
  functions [GenerateHackNightPlan]
  args {
    eventDescription #"
Join Us for the Hack Night at GitHub!

​​​Get ready for an exciting evening of hacking, networking, and innovation! Hosted at GitHub, Presented by Weaviate, this event is all about exploring the potential of AI and creating impactful solutions alongside fellow developers.

​​​🎤 Lightning Talks

    ​​​Insights and inspiration from top AI companies

        ​Weaviate

        ​FriendliAI

        ​dltHub

        ​Continue

        ​Antispace

    ​​​Learn how the latest advancements in AI agent frameworks and model deployment can take your projects further.

​​​🎮 Community Demos

    ​​​Share your creations, show off your projects, and inspire others during the demo session.

​​​🤝 Network & Collaborate

    ​​​Meet like-minded developers, share ideas, and make connections that could last a lifetime.

​​​🎁 Exciting Prizes

    ​​​Prizes are still being finalized but expect exciting rewards for challenge winners and demo presenters.

​​​Event Schedule:

    ​​​4:00 PM: Doors open – Pick up your challenge materials, grab some food, and start networking.

    ​​​5:00 PM: Lightning Talks – Hear from hosting companies and learn about opportunities.

    ​​​5:30 PM: Hacking Time (2.5 hours of innovation and collaboration).

    ​​​8:00 PM: Community Demos – Show what you’ve built!

    ​​​8:30 PM: Wrap-up & Closing.
    "#
  }
}