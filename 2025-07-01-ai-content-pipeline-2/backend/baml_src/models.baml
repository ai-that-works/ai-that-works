// Video content generation models

class EmailDraft {
  subject string
  body string @description(#"
    use triple quotes for multi-line strings
  "#)
  call_to_action string
}

class TwitterThread {
  tweets string[]
  hashtags string[]
}

class LinkedInPost {
  content string
  hashtags string[]
}