test EmailStructure {
  functions [GenerateEmailStructure]
  args {
    summary {
      main_takeaways [
        "Optimize prompts by shifting complex generation tasks to deterministic code.",
        "Reduce LLM token usage by outputting indexes or aliases instead of full text.",
        "Improve LLM focus by providing clear indexes and structured input.",
        "Use inline comments (even in JSON) to guide LLM reasoning without adding extra output.",
        "Read the F***ing Prompt (RTFP) to understand how the LLM is interpreting instructions.",
        "Structure prompts rather than adding real-world examples, to keep the control over the results.",
        "Leverage 'broken' JSON and deterministic code to enable more natural LLM code generation.",
        "Don't force LLMs to adopt a role, instead give it clear instructions.",
        "Don't have the LLM count. Pre-process your data and pass in the count, or create deterministic code that enforces the constraints.",
        "Focus on actionable insights by structuring output to match specific needs and workflows."
      ],
      key_topics [
        "Prompt engineering",
        "Token efficiency",
        "Structured outputs",
        "LLM reasoning",
        "Busted JSON",
        "Classification Optimization",
        "Deterministic Code vs. LLM Generation",
        "LLM Sampling Nuances",
        "Zero-Shot Learning with Structure"
      ],
      bullet_points [
        "Replace long, complex URLs with content indexes for citations.",
        "In diarization, output dialogue indexes instead of repeating the entire transcript.",
        "Use inline comments as guiding principles for reasoning steps.",
        "Always read the prompt to identify areas for optimization.",
        "Favor structural guidance over few-shot learning.",
        "Allow the LLM to generate more natural outputs, even if it means 'broken' JSON, and handle parsing deterministically.",
        "Favor structured outputs as opposed to relying on spitting out strings.",
        "Use separate pipelines for cleaning up or evaluating results in specific steps.\"\n    \"Don't have the LLM perform tasks that it is not good at (counting, deterministic lookups, etc."
      ]
    }
    structure {
  subject #"Cracking the Prompting Interview: Tips and Tricks from Vaibhav & Dex!"#
  we_covered #"a grab bag of small tips and tricks that are reusable across problem spaces, and like lower level advice that you can apply to lots of problems."#
  quick_recap [
    "Labels: Use indexes instead of full UIDs/URLs to improve reliability and token efficiency. Remap programmatically.",
    "Diarization: Don't emit the full transcript. Use indexes of the transcript to reduce token count and improve focus.",
    "In-line Comments: Use comments to guide reasoning and improve output, but consider impact on parsing.",
    "RTFP: Read the F**king Prompt! Always read carefully when debugging or iterating.",
    "Few-Shot Structure: Use few-shot prompting to define structure, but not necessarily content.",
    "Cogen: When generating code, let models output content naturally rather than forcing strict formats. It improves the quality."
  ]
  one_thing_to_remember #"Don’t try to be clever with token generation. Let the model pick the best token."#
  next_session #"Our next session on [July 15th 2025] will be all about \"Generating AI powered Content with LLMs \" – exploring how to use LLMs to generate content for various use cases. \nSign up here: https://lu.ma/ai-that-works-12"#
}
  }
}

test Marriedguan {
  functions [GenerateEmailDraft]
  args {
    next_session {
      event_name #"Generating AI powered Content with LLMs"#
      event_date #"July 15th 2025"#
      event_time #"10:00 AM"#
      invite_link #"https://lu.ma/ai-that-works-12"#
      description #"In this session, we'll explore how to use LLMs to generate content for various use cases. We'll cover topics like content creation, content curation, and content optimization."#

    }
    summary {
      bullet_points [
        #"Use indexes instead of full text/URLs when possible to improve reliability"#,
        #"Let models output content naturally rather than forcing strict formats"#,
        #"Add clear schemas and structure to guide responses"#,
        #"Read prompts carefully when debugging issues"#,
        #"Consider both token efficiency and output quality"#,
        #"Use comments and reasoning steps to improve output quality"#,
        #"Test prompts with real production data"#
      ]
      key_topics [
        #"Label and citation handling"#,
        #"Diarization techniques"#,
        #"Code generation"#,
        #"Prompt debugging"#,
        #"Token efficiency"#,
        #"Structured outputs"#,
        #"Real-world applications"#
      ]
      main_takeaways [
        #"Don't force models to generate long sequences of meaningless tokens (like URLs) - use indexes or aliases instead"#,
        #"Let models output content in their natural format rather than forcing strict JSON when possible"#,
        #"Always read your prompts carefully (RTFP) when debugging or improving them"#,
        #"Use structured outputs and clear schemas to guide model responses"#,
        #"Consider token efficiency but don't sacrifice quality - find the right balance"#
      ]
      timed_data [
        {
          end_time #"00:15:00"#
          start_time #"00:00:00"#
          summary #"Discussion of labels and citations in prompting, focusing on how to handle URLs and long token sequences efficiently. Introduced technique of using indexes instead of full URLs to reduce token usage and improve accuracy."#
        },
        {
          end_time #"00:30:00"#
          start_time #"00:15:00"#
          summary #"Coverage of diarization techniques for speaker identification in transcripts. Demonstrated how to use structured outputs and indexes instead of raw text to improve efficiency and accuracy."#
        },
        {
          end_time #"00:45:00"#
          start_time #"00:30:00"#
          summary #"Discussion of code generation techniques, focusing on allowing models to output code naturally rather than forcing JSON structure. Covered importance of reading prompts carefully (RTFP)."#
        },
        {
          end_time #"01:00:00"#
          start_time #"00:45:00"#
          summary #"Practical examples of improving prompts for real use cases, including event planning and video editing applications."#
        }
      ]
    }
    transcript #"
      WEBVTT
      
      1
      00:00:00.000 --> 00:00:23.139
      Dexter Horthy: You. We've seen this in like SQL generation. And maybe this is a tactic we can talk about today. But like we've seen it like SQL. Generation. Okay, have the model generate a Json object that can be determined turned into a SQL. Query for Svgs. The Tl. Draw. Guy was talking about this at AI engineer last week have the model generate a structured object that it's good at writing, that then deterministic code can turn into an Svg. And I think.
      
      2
      00:00:23.140 --> 00:00:35.660
      Dexter Horthy: have the model generate code that then you can like bake. It's like creating different views of the same thing. And then, once that's baked, then you can deterministically execute that code with the programming Runtime.
      
      3
      00:00:36.470 --> 00:00:37.040
      Vaibhav Gupta: Yeah.
      
      4
      00:00:37.240 --> 00:00:47.522
      Vaibhav Gupta: alright. Well, with that, let's get started. My name is Bye, Bob. This is Dexter. We've been doing this every week for the last few weeks now.
      
      5
      00:00:47.890 --> 00:00:49.769
      Dexter Horthy: Months we started in March. Dude.
      
      6
      00:00:49.770 --> 00:00:54.679
      Vaibhav Gupta: Oh, wow, yes, but we took a break, so I don't know if that counts. The break is where I define the line.
      
      7
      00:00:55.143 --> 00:01:07.880
      Vaibhav Gupta: But regardless. The whole point of this, these episodes of AI that works is to talk about real practical AI applications where we don't just talk about high level stuff, but really try and show the code behind how things work.
      
      8
      00:01:08.230 --> 00:01:32.249
      Vaibhav Gupta: We've talked about a bunch of things in the past from Mcp. Servers with 10,000 plus tools to 12 factor agents by Dexter all the way to human. Learn how to use humans as tools, and then just really how to think about prompts. But today I think we want to do something that was different. It's going to be a lot more varied in conversation than our previous conversations which are all about focusing on one depth thing. Today, we want to talk about just prompting as a whole.
      
      9
      00:01:32.580 --> 00:01:37.440
      Vaibhav Gupta: Nothing. Fancy, just plain old prompting, and many of you
      
      10
      00:01:38.244 --> 00:01:43.190
      Vaibhav Gupta: and actually, Dexter, do you want to give a little precursor while I get this screen recording up.
      
      11
      00:01:43.430 --> 00:02:01.810
      Dexter Horthy: Well, I think, like many of the things that we end up talking about, you can take like what is a really simple problem that folks kind of can look at and just say, Oh, that's solved, like like classification. It's like, Okay, I know how to pass the Lm. A list of labels and get it to output one of those labels with structured outputs or something like that. And then you go and you look under the hood, and it's like, Oh.
      
      12
      00:02:01.810 --> 00:02:30.180
      Dexter Horthy: like, actually, there's a lot of room where I thought the ceiling was like, Okay, here's the techniques. Here's how you do it. There's so much more room to basically open up the box and rip out all the wires and redo everything, and like engineer it to get much better results. And I think, like the core of that is always prompting. And so I'm really excited today to learn about both, like just some basic techniques framed in terms of certain types of problems.
      
      13
      00:02:30.180 --> 00:02:48.749
      Dexter Horthy: And I think today one of the things that it will be cool is we're not going to talk as much about like one big overarching problem, like we usually do. We're just going to give you a grab bag of small tips and tricks that are reusable across problem spaces, and like lower level advice that you can apply to lots of problems.
      
      14
      00:02:48.750 --> 00:03:01.780
      Dexter Horthy: And I think hopefully, if folks are down, I think we put a thread in the boundary discord. If anyone wants to share their prompts. The most I've ever learned about prompt engineering is showing 5 of AI applications that I've written.
      
      15
      00:03:01.780 --> 00:03:05.830
      Dexter Horthy: and having him roast my prompt and tell me what we're doing wrong.
      
      16
      00:03:06.923 --> 00:03:12.929
      Vaibhav Gupta: Actually, with that. What I'll do is in the thing in here. I will actually just post a link to this thread
      
      17
      00:03:13.190 --> 00:03:18.010
      Vaibhav Gupta: copy thread, and I'll post this in chat.
      
      18
      00:03:18.200 --> 00:03:19.090
      Vaibhav Gupta: If
      
      19
      00:03:19.507 --> 00:03:33.520
      Vaibhav Gupta: anyone wants, they're welcome to post their prompts that they want to share. This will be recorded and like. Just post it on here. We'll fix your prompts at the end, and we'll just show you how we would think about them doesn't mean that they'll necessarily get better. It might just give you another technique or 2.
      
      20
      00:03:33.940 --> 00:03:44.230
      Vaibhav Gupta: But with that, let's go into the topic cracking the prompting interview. I think prompting is literally like software engineering. And we're just gonna use the same techniques to do a couple of things off the bat.
      
      21
      00:03:44.350 --> 00:03:49.830
      Vaibhav Gupta: So let's start off with a very common problem that I always see, which is always
      
      22
      00:03:49.950 --> 00:03:53.450
      Vaibhav Gupta: the 1st one that I'm going to talk about, which is like labels.
      
      23
      00:03:54.350 --> 00:03:59.060
      Vaibhav Gupta: And this I think the most common example of this problem that I see is citations.
      
      24
      00:03:59.240 --> 00:04:10.120
      Vaibhav Gupta: So imagine that I have a prompt, my prompt will have a bunch of text that I refer to it, and for the context of rag with the rag, I will have it. Give me like the URL, or something attached to it.
      
      25
      00:04:11.010 --> 00:04:12.739
      Vaibhav Gupta: and I'll have a bunch of these
      
      26
      00:04:13.670 --> 00:04:22.180
      Vaibhav Gupta: along the way. So I'd like a URL with some data. And then I want to go get that. And somehow, in my answer. I want the Llm. To give me out. The URL.
      
      27
      00:04:23.600 --> 00:04:24.240
      Vaibhav Gupta: This
      
      28
      00:04:24.760 --> 00:04:30.110
      Vaibhav Gupta: is this a problem that I resonates with this couple of people? Does anyone have ideas for how we could make this better.
      
      29
      00:04:34.630 --> 00:04:38.340
      Vaibhav Gupta: If not, we'll just go right into it. If today's session is, gonna be.
      
      30
      00:04:38.340 --> 00:04:42.840
      Dexter Horthy: Are you? Gonna are you gonna replace the URL with a sentinel token.
      
      31
      00:04:43.630 --> 00:04:53.659
      Vaibhav Gupta: Kind of, yeah, exactly. Because what I want is, I want the answer that we over here to be an answer. But I want to include the citations that are that remap to that specific thing.
      
      32
      00:04:54.080 --> 00:05:01.790
      Vaibhav Gupta: Now, the problem is, as we all know, Urls can be really, really funky, like just the URL, for this Excalibrop is, I don't know. Let me see if I can share one
      
      33
      00:05:02.440 --> 00:05:06.950
      Vaibhav Gupta: like if I go to like. I don't know the random browser page. I probably have something open.
      
      34
      00:05:09.960 --> 00:05:12.660
      Vaibhav Gupta: Where'd it go? Sorry
      
      35
      00:05:14.850 --> 00:05:27.049
      Vaibhav Gupta: if I just go to like, for example, our Youtube channel. Let me just show some of these videos, these Urls are basically you. I could have this as a citation URL for my model. And let's just take a look at what it would mean for the model to generate this.
      
      36
      00:05:28.430 --> 00:05:34.279
      Vaibhav Gupta: Let's just go look at the Tokenizer, because I think this is the most important thing to think about. If a model can generate something accurately or not.
      
      37
      00:05:34.790 --> 00:05:56.929
      Vaibhav Gupta: this is what the model has to generate. There's a bunch of tokens. So these tokens make sense. It can probably do this. Youtube is a single token dot, Youtube is a single token. That's kind of interesting. Actually, I learned that today watch a single token. We're good question. Mark V is a single token which also probably makes sense, because Youtube probably is a predominant force in the tokenizer for some reason. But everything else here breaks down.
      
      38
      00:05:57.290 --> 00:05:58.390
      Vaibhav Gupta: This ends up.
      
      39
      00:05:58.390 --> 00:05:59.389
      Dexter Horthy: And this is.
      
      40
      00:05:59.750 --> 00:06:08.299
      Dexter Horthy: there's like models can generate a string. If you type in that string, you say, Hey, model, make this string for me, it's going to make it. But your point is basically that like
      
      41
      00:06:08.630 --> 00:06:17.549
      Dexter Horthy: the more tokens that you're asking the model to generate accurately the more kind of effort it has to put on that, and the the less likely it's going to get it right.
      
      42
      00:06:18.020 --> 00:06:21.570
      Vaibhav Gupta: Exactly so in order for the model to get this part of the URL correct
      
      43
      00:06:21.820 --> 00:06:33.830
      Vaibhav Gupta: specifically, it has to generate 10 tokens perfectly. If we remove this part, let's assume it'll get question. Mark V. Correct. It has to get 8 tokens perfectly correct. If it messes up in any of these, it becomes a useless link.
      
      44
      00:06:34.580 --> 00:06:37.750
      Vaibhav Gupta: So how can we change that? Well, we can do something really, really simple.
      
      45
      00:06:38.310 --> 00:06:41.279
      Vaibhav Gupta: And I will just use Youtube along the way.
      
      46
      00:06:41.770 --> 00:06:44.350
      Vaibhav Gupta: And I'll write a basic prompt that does this
      
      47
      00:06:44.630 --> 00:06:49.480
      Vaibhav Gupta: and tries to go about this whoops.
      
      48
      00:06:50.450 --> 00:06:56.410
      Vaibhav Gupta: So we're going to write a question, new file like labels. Dot, Aml.
      
      49
      00:06:57.300 --> 00:07:02.240
      Vaibhav Gupta: I'm gonna have a function that's gonna say, given like answer question.
      
      50
      00:07:02.670 --> 00:07:08.490
      Vaibhav Gupta: I'm gonna say, here's a question. I'm gonna give it a list of links or content.
      
      51
      00:07:14.860 --> 00:07:19.480
      Vaibhav Gupta: I'll say like this will have like a URL, which will be a string
      
      52
      00:07:19.930 --> 00:07:22.450
      Vaibhav Gupta: and then content, which would be a string. And then
      
      53
      00:07:23.900 --> 00:07:37.890
      Vaibhav Gupta: what? What we'll return. Here is some answer, and then citations sharing array at definition list of Urls
      
      54
      00:07:39.270 --> 00:07:41.579
      Vaibhav Gupta: that are relevant.
      
      55
      00:07:41.700 --> 00:07:55.400
      Vaibhav Gupta: Okay, open AI Gpt. 4. 0, great and ctx dot output format.
      
      56
      00:07:56.690 --> 00:08:01.169
      Vaibhav Gupta: Sorry I'm on a live prompt. So I'm gonna try and be as fast as possible.
      
      57
      00:08:01.910 --> 00:08:03.950
      Vaibhav Gupta: All user question.
      
      58
      00:08:04.910 --> 00:08:11.539
      Dexter Horthy: Okay. So output format is, you're telling it how to output the answer.
      
      59
      00:08:12.530 --> 00:08:13.430
      Vaibhav Gupta: Exactly.
      
      60
      00:08:13.950 --> 00:08:18.729
      Dexter Horthy: And you're and you're putting the output format and the relevant content into the system prompt.
      
      61
      00:08:19.110 --> 00:08:22.060
      Dexter Horthy: And then we're putting the user. The question in the user prompt.
      
      62
      00:08:23.070 --> 00:08:23.960
      Vaibhav Gupta: Exactly.
      
      63
      00:08:24.190 --> 00:08:27.299
      Vaibhav Gupta: So I'm gonna do this. So now there's my prompt
      
      64
      00:08:28.690 --> 00:08:37.279
      Vaibhav Gupta: and I will literally just ask her sort of generate me a test case for this rag use case
      
      65
      00:08:37.860 --> 00:08:42.610
      Vaibhav Gupta: use resume.
      
      66
      00:08:46.090 --> 00:08:49.600
      Dexter Horthy: They are all the same file. They're all gonna have a test case in them.
      
      67
      00:08:49.820 --> 00:08:58.780
      Vaibhav Gupta: I'm gonna move this username as as a reference for how that all works.
      
      68
      00:08:59.420 --> 00:09:01.580
      Vaibhav Gupta: So I'll just have to generate a test case really fast.
      
      69
      00:09:02.310 --> 00:09:13.099
      Vaibhav Gupta: and then it'll just go do something for me, but we can see how like and then this takes a little bit, but we can see how like the model might struggle to go. Do something great except
      
      70
      00:09:13.250 --> 00:09:14.040
      Vaibhav Gupta: cool.
      
      71
      00:09:14.820 --> 00:09:16.236
      Vaibhav Gupta: Let's go do this.
      
      72
      00:09:16.590 --> 00:09:20.527
      Dexter Horthy: Oh, man, are you gonna make these urls really freaking crazy? And then,
      
      73
      00:09:20.970 --> 00:09:23.029
      Dexter Horthy: see if we can actually get the model to screw it up.
      
      74
      00:09:23.560 --> 00:09:24.619
      Vaibhav Gupta: Use this.
      
      75
      00:09:26.130 --> 00:09:28.230
      Vaibhav Gupta: So this is one Youtube, URL
      
      76
      00:09:28.980 --> 00:09:32.369
      Vaibhav Gupta: and I will copy another Youtube URL from a different video.
      
      77
      00:09:36.700 --> 00:09:44.820
      Vaibhav Gupta: And I will point this out. It's not even a matter of like the model will screw this up. The point here is, it doesn't matter if the model does this perfectly or not
      
      78
      00:09:44.990 --> 00:09:49.429
      Vaibhav Gupta: the point that matters is, the model might screw it up.
      
      79
      00:09:50.240 --> 00:10:03.049
      Vaibhav Gupta: and if it screws it up I have no guarantee on this end. So there's small things that I can do. So. Now that I have some citation thing in here, I can do something nice in my python code to help reduce some of these errors.
      
      80
      00:10:04.950 --> 00:10:13.590
      Dexter Horthy: Oh, you can put like a guard. This is from the Eval saying, you put a runtime guard of like, hey? If it outputs a URL that wasn't in our input set, bounce it back and tell it to try again.
      
      81
      00:10:13.590 --> 00:10:17.017
      Vaibhav Gupta: Let me actually open just this one folder really fast
      
      82
      00:10:18.680 --> 00:10:20.469
      Vaibhav Gupta: that way. It's only a little bit cleaner.
      
      83
      00:10:21.100 --> 00:10:21.900
      Vaibhav Gupta: There you go.
      
      84
      00:10:22.660 --> 00:10:28.100
      Vaibhav Gupta: Otherwise Python versions don't work for Monorepos, which is the worst thing that Python is committed.
      
      85
      00:10:28.650 --> 00:10:33.919
      Dexter Horthy: We're getting there. I think the UV dot python stuff might actually eventually fix it.
      
      86
      00:10:34.690 --> 00:10:36.310
      Vaibhav Gupta: I really hope so.
      
      87
      00:10:39.700 --> 00:10:42.840
      Vaibhav Gupta: So. One thing I can do is I can literally just get the answer
      
      88
      00:10:43.240 --> 00:10:49.025
      Vaibhav Gupta: equals this, and then I can say like for URL in answer
      
      89
      00:10:49.770 --> 00:11:00.709
      Vaibhav Gupta: answer, dot citations. I somehow assert that the URL starts with this. I could like build some small search. I could, I could assert that the Urls are actually natural. Content array that comes in there.
      
      90
      00:11:05.070 --> 00:11:05.910
      Vaibhav Gupta: Oh.
      
      91
      00:11:07.770 --> 00:11:09.730
      Dexter Horthy: I got it I'll I'll get the link.
      
      92
      00:11:10.898 --> 00:11:21.090
      Vaibhav Gupta: So we can actually go build this URL right for us. Now, we can actually go further. The problem is right over here. This Urls, as we saw, have a problem with how the models to generate them.
      
      93
      00:11:22.240 --> 00:11:27.140
      Vaibhav Gupta: So let's go fix that actually. And let's say, this is our actual Urls.
      
      94
      00:11:30.820 --> 00:11:39.720
      Vaibhav Gupta: Oh, from Bamo, client dot types import content.
      
      95
      00:11:40.580 --> 00:11:49.239
      Vaibhav Gupta: Now, what I can do here is, instead of actually putting this URL, as is, I could literally put a I could 1st change this completely
      
      96
      00:11:49.620 --> 00:11:55.599
      Vaibhav Gupta: and say, what I actually want to do is I won't list a return of citation. I will actually list an index
      
      97
      00:11:56.990 --> 00:11:59.830
      Vaibhav Gupta: index of the content.
      
      98
      00:12:01.670 --> 00:12:07.130
      Vaibhav Gupta: And now that this returns an index of the content, what I will do here is literally just print this out content
      
      99
      00:12:09.010 --> 00:12:15.229
      Vaibhav Gupta: loop dot index 0 content idx. And now my prompt looks like this.
      
      100
      00:12:15.700 --> 00:12:24.979
      Vaibhav Gupta: instead of actually dumping the actual URL, I just say, content. Idx 0, 0. I can actually put like dashes here, separators. I can put them beforehand, because that might actually be better
      
      101
      00:12:27.510 --> 00:12:28.730
      Vaibhav Gupta: content.
      
      102
      00:12:29.670 --> 00:12:41.700
      Vaibhav Gupta: I can do this and now it's actually called content out content, one content. 0. And now I just remove the idea of the URL completely from the model, and the model will not do this, and when I go run this.
      
      103
      00:12:43.330 --> 00:12:49.019
      Vaibhav Gupta: what we'll find is great. We get 0 and one because those are relevant indexes. And like, let's make up a 3rd one. That doesn't matter.
      
      104
      00:12:52.810 --> 00:12:59.660
      Vaibhav Gupta: Europe is pretty cool and has great pasta.
      
      105
      00:13:01.580 --> 00:13:09.350
      Vaibhav Gupta: and ideally, it shouldn't pick up the right content. It should only pick up 0 and one. And now what I can do in my code, instead of doing it in the model is, I can convert
      
      106
      00:13:09.550 --> 00:13:13.509
      Vaibhav Gupta: the URL into the actual citation.
      
      107
      00:13:13.620 --> 00:13:15.199
      Vaibhav Gupta: So now I can just say, like
      
      108
      00:13:15.410 --> 00:13:18.870
      Vaibhav Gupta: content of URL Dot, what is it
      
      109
      00:13:19.430 --> 00:13:30.320
      Vaibhav Gupta: content of URL dot URL, or the actual URL that I actually want? So it becomes an index based lookup instead of a real one. So the idea is, you really don't you really want to do your best.
      
      110
      00:13:30.820 --> 00:13:35.549
      Vaibhav Gupta: and to not rely on models generating long sequences of tokens
      
      111
      00:13:35.680 --> 00:13:40.349
      Vaibhav Gupta: that don't make sense for the model to actually, intuitively think about similar.
      
      112
      00:13:40.350 --> 00:13:45.370
      Dexter Horthy: No meaning. There's no meaning baked into that random string of characters. It's just a pointer.
      
      113
      00:13:45.640 --> 00:13:57.050
      Vaibhav Gupta: Exactly. And if you can go further, and if you go back to our content about dynamic enums, you could, for example, make this a dynamic enum that then has an alias that gets mapped back to the actual file.
      
      114
      00:13:57.050 --> 00:14:07.779
      Dexter Horthy: Yeah, I was. Gonna say, we could go into all of the fancy bamel features that make this even easier. I am. Gonna say we are 20 min in. So if you, if you want to move on to the next tip, or do you want to wrap this one up or or do you have more
      
      115
      00:14:08.440 --> 00:14:09.110
      Dexter Horthy: stuff?
      
      116
      00:14:09.280 --> 00:14:10.320
      Dexter Horthy: Perfect.
      
      117
      00:14:10.320 --> 00:14:15.459
      Vaibhav Gupta: It's don't use sequences of tokens that don't make sense for the model. Go update it on your own.
      
      118
      00:14:15.880 --> 00:14:20.020
      Dexter Horthy: We got one question. Symbol tuning also applies here.
      
      119
      00:14:20.020 --> 00:14:26.520
      Vaibhav Gupta: Exactly. Symbol tuning is exact. Same thing. Docs will cover that. Can't talk about that right now because of time constraints.
      
      120
      00:14:26.920 --> 00:14:29.010
      Vaibhav Gupta: We're gonna do another one diarization.
      
      121
      00:14:29.440 --> 00:14:39.260
      Vaibhav Gupta: So we've all seen diarization examples. We're like, do this make a make a transcript do diarization
      
      122
      00:14:39.890 --> 00:14:49.639
      Vaibhav Gupta: diarization function, use labels of ammo as an example.
      
      123
      00:14:50.490 --> 00:14:55.030
      Dexter Horthy: Do you want to do a quick whiteboard on like? What? What do we mean by diarization?
      
      124
      00:14:55.798 --> 00:14:59.480
      Vaibhav Gupta: Will go do this. I'll describe some words over here.
      
      125
      00:15:00.210 --> 00:15:02.040
      Dexter Horthy: So let's talk about diarization.
      
      126
      00:15:02.530 --> 00:15:13.470
      Vaibhav Gupta: Diarization. Diarization. Diarization is this idea that we have audio coming in and we want to turn the audio snippets into like a
      
      127
      00:15:13.670 --> 00:15:21.859
      Vaibhav Gupta: speaker plus transcript section. So each of these will always have a speaker, and each of these will, and then transform into like, who said, What
      
      128
      00:15:22.020 --> 00:15:25.099
      Vaibhav Gupta: so idea is, most of these sequences come from.
      
      129
      00:15:26.166 --> 00:15:33.579
      Vaibhav Gupta: And Mo, what most of these will do is they'll basically say, literally, say, Speaker, 0 speaker, one speaker, 0 speaker, one
      
      130
      00:15:34.657 --> 00:15:47.990
      Vaibhav Gupta: and you might actually want to go do something more than that, because you might be having a conversation between a nurse and a patient. So you might actually want to say, speaker, one is a nurse speaker 2 is a patient and transform your transcript to that.
      
      131
      00:15:48.400 --> 00:15:53.284
      Vaibhav Gupta: I'm going to show you a prompting trip that is going to reduce the amount of
      
      132
      00:15:53.860 --> 00:16:01.219
      Vaibhav Gupta: text that we might have to generate by an order of magnitude to solve this problem. Because if I want to go from person one
      
      133
      00:16:01.460 --> 00:16:08.660
      Vaibhav Gupta: to speaker like nurse versus patient
      
      134
      00:16:12.280 --> 00:16:14.570
      Vaibhav Gupta: versus like
      
      135
      00:16:14.800 --> 00:16:21.400
      Vaibhav Gupta: other, because maybe their husband or wife spoke up into it in the middle of it. I want to know exactly who these personas are.
      
      136
      00:16:21.740 --> 00:16:24.010
      Vaibhav Gupta: So let's go do that, and.
      
      137
      00:16:24.010 --> 00:16:34.920
      Dexter Horthy: Real real quick is, there is, does it? Is? I imagine this is probably equivalent whether you're doing audio or raw, just like a raw transcript of a conversation right.
      
      138
      00:16:35.470 --> 00:16:45.739
      Vaibhav Gupta: Yes, so I'm gonna assume that the transcript is, gonna have a speaker. Let's just say the transcript is on. Let's simplify this a little bit. Let's say the transcript is literally just a string.
      
      139
      00:16:47.250 --> 00:16:51.189
      Vaibhav Gupta: and what I want to do is I want to identify the speakers that exist for each of these
      
      140
      00:16:51.660 --> 00:16:54.959
      Vaibhav Gupta: right? So the transcript is literally just going to be a string.
      
      141
      00:16:55.340 --> 00:16:58.949
      Vaibhav Gupta: And I I have no other information about it.
      
      142
      00:17:00.801 --> 00:17:07.980
      Vaibhav Gupta: Transcript will turn into that, and then what I want is I want to return a diarized transcript which is going to be a bunch of speaker. Segments don't need this.
      
      143
      00:17:08.510 --> 00:17:15.630
      Vaibhav Gupta: and this will just have Speaker string text. And you might even say that this is like nurse.
      
      144
      00:17:16.650 --> 00:17:18.969
      Vaibhav Gupta: doctor, patient or other.
      
      145
      00:17:19.550 --> 00:17:21.790
      Vaibhav Gupta: So let's let's like right here.
      
      146
      00:17:22.359 --> 00:17:22.969
      Dexter Horthy: Cool.
      
      147
      00:17:26.189 --> 00:17:29.119
      Vaibhav Gupta: Identify, identify the speakers.
      
      148
      00:17:30.719 --> 00:17:34.629
      Vaibhav Gupta: Ctx dot output format.
      
      149
      00:17:36.229 --> 00:17:42.899
      Vaibhav Gupta: And then user, okay, cool. That's probably good enough.
      
      150
      00:17:43.359 --> 00:17:44.959
      Vaibhav Gupta: Oh, that's actually pretty cool.
      
      151
      00:17:48.029 --> 00:17:48.769
      Vaibhav Gupta: Let's change.
      
      152
      00:17:48.770 --> 00:17:50.960
      Dexter Horthy: But you actually just want the raw text, right?
      
      153
      00:17:51.230 --> 00:17:55.009
      Vaibhav Gupta: Yeah, so I will. Oh, yeah, that's true. Thank you for identifying that, Dexter.
      
      154
      00:17:55.867 --> 00:17:59.190
      Vaibhav Gupta: Actually, I think, test cases converted correctly.
      
      155
      00:18:08.640 --> 00:18:09.920
      Vaibhav Gupta: how are you?
      
      156
      00:18:10.300 --> 00:18:15.110
      Vaibhav Gupta: I'm hurt my knee hearts.
      
      157
      00:18:16.000 --> 00:18:17.170
      Vaibhav Gupta: I'm sorry.
      
      158
      00:18:18.300 --> 00:18:25.119
      Dexter Horthy: Sorry. So so this is already. Has the speakers identified, though right like.
      
      159
      00:18:25.120 --> 00:18:27.130
      Vaibhav Gupta: But it doesn't tell me who's who.
      
      160
      00:18:29.130 --> 00:18:36.559
      Dexter Horthy: Okay is, so would this technique work like, is this applicable also to just a
      
      161
      00:18:36.730 --> 00:18:43.680
      Dexter Horthy: like non, like, if I just have a a stream of text, and I don't. It's not already split up by speaker.
      
      162
      00:18:44.870 --> 00:18:45.529
      Dexter Horthy: I guess.
      
      163
      00:18:45.940 --> 00:18:50.551
      Dexter Horthy: Okay, so this just assumes you have turn detection, but not necessarily
      
      164
      00:18:51.320 --> 00:18:57.620
      Vaibhav Gupta: Let's say we don't know the speaker. We don't know anything about this. What we really want to do is we want to go and convert this in a really quick way.
      
      165
      00:18:58.529 --> 00:19:15.780
      Vaibhav Gupta: So I'm gonna go change it. It's been hurting for 3 days now fix. He's been complaining about it for a while. So this is interesting because there might be a lot of other content here. So let's just see, firstly, what the what, the what the raw thing ends up being.
      
      166
      00:19:17.020 --> 00:19:19.500
      Dexter Horthy: Yeah, cool. This.
      
      167
      00:19:19.710 --> 00:19:24.669
      Vaibhav Gupta: This seems kind of interesting. It's like cool. It has other. It has all these other things in here.
      
      168
      00:19:24.900 --> 00:19:27.590
      Vaibhav Gupta: Let's try and make this better really fast.
      
      169
      00:19:28.757 --> 00:19:44.199
      Vaibhav Gupta: And I'm gonna combine like 2 or 3 different of the prompting tips right in one as I go. So the 1st thing I'm gonna notice is, Hey, this is probably not very useful. So let's try and just like fix this.
      
      170
      00:19:44.200 --> 00:19:45.840
      Dexter Horthy: What part of it is not useful.
      
      171
      00:19:45.840 --> 00:19:48.739
      Vaibhav Gupta: Well, one, I'm outputting the whole transcript over and over again.
      
      172
      00:19:49.470 --> 00:19:50.579
      Vaibhav Gupta: That sounds bad.
      
      173
      00:19:51.140 --> 00:19:53.690
      Vaibhav Gupta: Let's see if we can do this in a slightly better way.
      
      174
      00:19:54.363 --> 00:20:01.020
      Vaibhav Gupta: So what I'm going to do is I'm gonna say, dialogue index.
      
      175
      00:20:01.240 --> 00:20:01.950
      Vaibhav Gupta: And
      
      176
      00:20:02.670 --> 00:20:08.269
      Vaibhav Gupta: so I'm gonna give it. Give it the dialog index. And here I'm just gonna like, write this in my prompt, really fast.
      
      177
      00:20:08.930 --> 00:20:12.017
      Vaibhav Gupta: So I don't have to think about this. But
      
      178
      00:20:12.760 --> 00:20:14.409
      Vaibhav Gupta: the right way to do this is
      
      179
      00:20:14.860 --> 00:20:17.040
      Vaibhav Gupta: honestly to just make this thing an array.
      
      180
      00:20:20.534 --> 00:20:21.049
      Vaibhav Gupta: Sorry
      
      181
      00:20:28.500 --> 00:20:31.560
      Vaibhav Gupta: I love cursor, and we'll make this an array.
      
      182
      00:20:31.920 --> 00:20:38.860
      Vaibhav Gupta: And now, instead of dumping the Transcript out as we are what we'll do as well as a or a line and transcript printed the line.
      
      183
      00:20:39.300 --> 00:20:44.670
      Vaibhav Gupta: And now what we'll also say is this loop dot index 0 dialogue.
      
      184
      00:20:47.060 --> 00:20:50.769
      Vaibhav Gupta: This add an extra space in there and then we'll add that in.
      
      185
      00:20:51.210 --> 00:20:53.220
      Vaibhav Gupta: So now what we'll.
      
      186
      00:20:53.220 --> 00:21:02.830
      sahil: An assumption that the the script is already an array, or are we just converting the script into an array like.
      
      187
      00:21:03.110 --> 00:21:09.939
      Vaibhav Gupta: You can just split by you can just split by. I'm assuming, if you have some way of a speaker, Colon. Here, you have a way to convert this into an array of some kind.
      
      188
      00:21:10.440 --> 00:21:11.150
      sahil: Okay.
      
      189
      00:21:11.430 --> 00:21:25.990
      Dexter Horthy: Yeah, I think I think in, yeah, I think the questions that a lot of people are asking is kind of the like, the real time, actual speech to text use cases. You don't have those like separators unless you're using like a separate like, turn detection model, basically.
      
      190
      00:21:26.270 --> 00:21:40.230
      Vaibhav Gupta: Yes, but most people should be using a turn detection model. So I'm assuming that you have that right now, you're analyzing a transcript in post. We can remove the speaker labels as well. So it's like a little bit more clear. It's like we just have all the statements that are literally speech to text per line of some kind.
      
      191
      00:21:40.560 --> 00:21:42.090
      Vaibhav Gupta: I'm gonna go run this now.
      
      192
      00:21:42.310 --> 00:21:43.750
      Vaibhav Gupta: Now you'll notice
      
      193
      00:21:44.030 --> 00:21:50.570
      Vaibhav Gupta: the model is actually really, really good at just bidding out the dialogue index, and who the who the speaker is. In each of these scenarios.
      
      194
      00:21:51.160 --> 00:21:54.129
      Dexter Horthy: Oh, so it doesn't have to re output the actual text itself.
      
      195
      00:21:54.130 --> 00:22:01.560
      Vaibhav Gupta: Exactly order of magnet you can imagine for long transcripts. This is an order of magnitude cheaper
      
      196
      00:22:01.870 --> 00:22:07.480
      Vaibhav Gupta: in terms of how much text that's output, and we can reduce this even further and just like aliases to like
      
      197
      00:22:07.910 --> 00:22:10.120
      Vaibhav Gupta: alias idx.
      
      198
      00:22:11.300 --> 00:22:15.779
      Vaibhav Gupta: And then it'll be a lot shorter. And now it's just now it's just outputting the index, and the speaker.
      
      199
      00:22:17.060 --> 00:22:17.420
      Dexter Horthy: I'm.
      
      200
      00:22:17.420 --> 00:22:18.020
      Vaibhav Gupta: And.
      
      201
      00:22:18.020 --> 00:22:21.630
      Dexter Horthy: A little curious what would happen if you just put it all as one big string.
      
      202
      00:22:22.310 --> 00:22:23.859
      Vaibhav Gupta: What do you mean? Oh.
      
      203
      00:22:23.860 --> 00:22:28.610
      Dexter Horthy: Like like, if you didn't split them out. I imagine it's probably not gonna work as well, but.
      
      204
      00:22:28.930 --> 00:22:42.880
      Vaibhav Gupta: The reason that this works a lot better is twofold one. I'm actually telling it the model what the index is. So the model has to go back and say, Let's look at what the model does turn by turn. It's going to 1st output idx 0,
      
      205
      00:22:43.190 --> 00:23:05.820
      Vaibhav Gupta: then all it has to do is in its token. During the attention mechanism the model goes back into its tokenizer, so it literally will go back through all the tokens and just say, Okay, what tokens I want to look at. I want to look at next 0. It's going to go in to say, Okay, I need to understand this part of this part of the segment, it's easier for it to focus. So even though it's a little redundant, it helps the model be a little bit more focused
      
      206
      00:23:06.080 --> 00:23:09.710
      Vaibhav Gupta: on its part. Now it's like, Okay, what? Who likely? Said this?
      
      207
      00:23:10.540 --> 00:23:26.409
      Vaibhav Gupta: And then it's like, and then it goes out and starts spitting out the next token spits out idx. So at the point of idx, now it says, Oh, what's the next idx I need? Oh, let me go back a couple tokens here is like that was 0. I probably need one. Next, we're reducing the burden on the model.
      
      208
      00:23:26.690 --> 00:23:30.190
      Vaibhav Gupta: That's the main. That's the main leverage here.
      
      209
      00:23:30.460 --> 00:23:36.670
      Vaibhav Gupta: The model at any point is able to do way less work, and then therefore output more. Does that make sense Dexter.
      
      210
      00:23:37.350 --> 00:23:38.699
      Dexter Horthy: Yeah, I got you cool.
      
      211
      00:23:39.060 --> 00:23:39.750
      Vaibhav Gupta: Cool.
      
      212
      00:23:40.290 --> 00:23:49.089
      Vaibhav Gupta: Now the thing is, we may not actually know exactly who's talking here like this other thing. We might have made a bug and not actually introduced other.
      
      213
      00:23:50.160 --> 00:23:54.710
      Vaibhav Gupta: And in this scenario what we'll find is likely the model.
      
      214
      00:23:55.790 --> 00:23:57.820
      Vaibhav Gupta: We'll do something just output. It's a nurse.
      
      215
      00:23:58.050 --> 00:24:00.389
      Vaibhav Gupta: it kind of hallucinated on its own.
      
      216
      00:24:01.010 --> 00:24:03.249
      Vaibhav Gupta: So we can actually just add other
      
      217
      00:24:03.780 --> 00:24:11.399
      Vaibhav Gupta: as a fallback. So we, the model doesn't tend to hallucinate. We want to prevent hallucinations when possible, and we do that by giving the model and out. That's the.
      
      218
      00:24:11.400 --> 00:24:33.350
      Dexter Horthy: And this is the same with all the all, the classifier examples that that we talk about. Right is like, classify the things you know you are good at classifying in the fastest, cheapest, most efficient way, and then allow the model to have an escape hatch, in which case you'll handle it in a different way, either by sending it to a human to classify or sending it to a bigger, smarter model, or whatever it is.
      
      219
      00:24:33.650 --> 00:24:40.320
      Vaibhav Gupta: Exactly. But now let's do another thing. Let's do another thing, clues, but that's some clues here.
      
      220
      00:24:40.560 --> 00:24:41.280
      Vaibhav Gupta: So I'm gonna.
      
      221
      00:24:41.280 --> 00:24:41.720
      Dexter Horthy: Reasoning.
      
      222
      00:24:41.720 --> 00:24:46.840
      Vaibhav Gupta: Things that I'm exactly. So I'm gonna help the model think about what it is. And it's literally just like
      
      223
      00:24:47.760 --> 00:24:50.190
      Vaibhav Gupta: it's literally just dumping the text here.
      
      224
      00:24:52.141 --> 00:24:59.110
      Vaibhav Gupta: And like this is not very useful. Add description, things that help inference.
      
      225
      00:24:59.430 --> 00:25:00.530
      Vaibhav Gupta: To.
      
      226
      00:25:01.310 --> 00:25:04.399
      Vaibhav Gupta: Let's just add a little bit more dialogue here, and we'll see what it does.
      
      227
      00:25:08.695 --> 00:25:13.750
      Vaibhav Gupta: let's say what might
      
      228
      00:25:14.982 --> 00:25:26.379
      Vaibhav Gupta: relevant. So let's so we're noticing that what it's doing is just outputting all the clues, but a lot of the times. It's kind of obvious who the speaker is. So let's just do this only, if not obvious.
      
      229
      00:25:28.717 --> 00:25:33.560
      Vaibhav Gupta: List out facts that help us.
      
      230
      00:25:35.250 --> 00:25:38.090
      Vaibhav Gupta: Identify, help us, analyze.
      
      231
      00:25:38.500 --> 00:25:47.359
      Dexter Horthy: Yeah. John's suggesting deductive reasoning steps, which I think is gets a little towards some of the stuff we've done in the past around like structured reasoning stuff.
      
      232
      00:25:47.670 --> 00:25:52.440
      Vaibhav Gupta: There who the speaker may be.
      
      233
      00:25:52.980 --> 00:25:55.470
      Vaibhav Gupta: I had a much better test case pulled up earlier.
      
      234
      00:25:56.270 --> 00:25:58.649
      Vaibhav Gupta: So and now you're noticing over here.
      
      235
      00:25:59.600 --> 00:26:00.020
      Dexter Horthy: Hmm.
      
      236
      00:26:00.020 --> 00:26:02.330
      Vaibhav Gupta: Now something a lot more interesting.
      
      237
      00:26:03.040 --> 00:26:10.769
      Vaibhav Gupta: It says Speaker 0 other because they don't know yet. Speaker, one uses personal pronouns indicating injury. That means that they're probably a patient
      
      238
      00:26:11.430 --> 00:26:16.580
      Vaibhav Gupta: speaking about the patient, so probably other along the way.
      
      239
      00:26:18.460 --> 00:26:25.099
      Vaibhav Gupta: So it's actually a lot more useful to actually go do this. And now we can have a lot more comp confidence behind what's happening.
      
      240
      00:26:25.960 --> 00:26:30.609
      Dexter Horthy: But it's also it's it's gotten. It's it's gotten worse at picking the ones where it was. The.
      
      241
      00:26:30.610 --> 00:26:33.159
      Prashanth Rao: The doctor, the doctor and nurse are worse.
      
      242
      00:26:33.650 --> 00:26:35.089
      Vaibhav Gupta: Yes, but
      
      243
      00:26:35.690 --> 00:26:45.479
      Vaibhav Gupta: that might be because when you really think about it, doctor and nurse are actually confusing, because how does it actually identify correctly between the doctor and the nurse.
      
      244
      00:26:46.720 --> 00:26:48.650
      Vaibhav Gupta: and we can go about this one more time.
      
      245
      00:26:48.910 --> 00:26:50.690
      Vaibhav Gupta: And if we actually go, look at this.
      
      246
      00:26:50.910 --> 00:26:58.770
      Vaibhav Gupta: If I were to read this transcript. There is no freaking way. I, as a human, would actually be able to know if it's actually a doctor or a patient doctor or not
      
      247
      00:27:00.160 --> 00:27:02.420
      Vaibhav Gupta: without knowing how many people are in the room.
      
      248
      00:27:03.880 --> 00:27:04.840
      Prashanth Rao: Very true.
      
      249
      00:27:05.150 --> 00:27:07.520
      Vaibhav Gupta: I could be talking to my brother.
      
      250
      00:27:07.520 --> 00:27:09.780
      Vaibhav Gupta: Exactly, exactly, and that's the.
      
      251
      00:27:09.780 --> 00:27:11.610
      Dexter Horthy: Could be my uncle talking shit.
      
      252
      00:27:12.360 --> 00:27:22.729
      Vaibhav Gupta: So whenever some, when you said doctor and patient got nurse, you're right. We intuitively felt that way. But remember, the model has no context around this. So let's add some more context.
      
      253
      00:27:22.730 --> 00:27:26.790
      Prashanth Rao: Sorry could you go to? So before you clear this out, could you go to the 3rd index? Index? Number 2?
      
      254
      00:27:27.900 --> 00:27:30.919
      Prashanth Rao: Yeah, this this time it seems to have gotten it.
      
      255
      00:27:31.350 --> 00:27:33.280
      Vaibhav Gupta: Because it's making assumptions.
      
      256
      00:27:33.420 --> 00:27:34.319
      Prashanth Rao: Yeah, yeah.
      
      257
      00:27:34.320 --> 00:27:36.779
      Vaibhav Gupta: About it right? It's made. But now we.
      
      258
      00:27:36.780 --> 00:27:41.590
      Dexter Horthy: Taking more from the prompt itself, like the actual output format, right.
      
      259
      00:27:41.590 --> 00:27:48.639
      Vaibhav Gupta: Exactly. It's literally just like, you're probably either doctor or patient, like there's no there's no way around this. But now that we force the model to be like
      
      260
      00:27:49.250 --> 00:27:53.159
      Vaibhav Gupta: who, if not only if not obvious, go list out facts.
      
      261
      00:27:54.040 --> 00:27:59.940
      Vaibhav Gupta: And in fact, the obvious answer for identifying speakers may be other in all scenarios.
      
      262
      00:28:00.970 --> 00:28:06.550
      Vaibhav Gupta: and that's what I would do if I had, I would unlabel everything. But then I would say, Oh.
      
      263
      00:28:07.200 --> 00:28:13.100
      Vaibhav Gupta: but now we know for sure that this one is a patient because it has been non obviously stated.
      
      264
      00:28:13.840 --> 00:28:16.850
      Vaibhav Gupta: But we can go further. We can make this a little bit better.
      
      265
      00:28:18.600 --> 00:28:47.060
      Vaibhav Gupta: There there were 4 people in the room, Dr. Josh, there's 5 h next, the friend unidentified.
      
      266
      00:28:48.460 --> 00:28:52.599
      Vaibhav Gupta: So we can go do this cause, maybe, for my Emr. I know exactly who visited.
      
      267
      00:28:53.240 --> 00:28:56.819
      Vaibhav Gupta: but I don't know. I don't have any information on the other person at all.
      
      268
      00:28:57.660 --> 00:29:04.820
      Vaibhav Gupta: So now let's add this in here and say for context.
      
      269
      00:29:12.300 --> 00:29:14.219
      Vaibhav Gupta: And now let's let's run this.
      
      270
      00:29:16.850 --> 00:29:20.260
      Vaibhav Gupta: And now what we find is that the model gets a lot better.
      
      271
      00:29:21.760 --> 00:29:36.690
      Dexter Horthy: Right? So you could. You could look at like, if you want to do this for a random event, you could go get the people off the Google Calendar event, and just inject that at the top, like, here's the people. And here's their domains. And here's, you know, 2 sentences of deep research about who this person is.
      
      272
      00:29:37.100 --> 00:29:53.039
      Vaibhav Gupta: Exactly. And this, this mechanism of how we felt like it got more inaccurate, and might have diverted us from actually exploring this prompt further is actually important to understand why the model did this step back, rethink and remember that the model did this? Because
      
      273
      00:29:53.230 --> 00:30:10.189
      Vaibhav Gupta: if I were to be completely objective. Show this to a random person to have tell them identify speakers. They also would likely pick other if they have to be like, if the choice would be wrong or be correct. I, too, would prefer to be not wrong, and just pick other, because other is never wrong.
      
      274
      00:30:11.640 --> 00:30:12.390
      Dexter Horthy: Cool.
      
      275
      00:30:13.870 --> 00:30:15.880
      Dexter Horthy: Are we gonna trip back? Takes today?
      
      276
      00:30:16.120 --> 00:30:20.489
      Vaibhav Gupta: I'll do that in a second. That's Tip number 2, where we use diarization.
      
      277
      00:30:20.610 --> 00:30:26.190
      Vaibhav Gupta: And I want to show one last variant of this trick. Which is these clues.
      
      278
      00:30:27.120 --> 00:30:39.480
      Vaibhav Gupta: So instead of outputting clues, we can just do this description as a precursor to the comment.
      
      279
      00:30:40.090 --> 00:30:45.945
      Vaibhav Gupta: as a precursor sort of comment to this field.
      
      280
      00:30:46.800 --> 00:30:47.970
      Vaibhav Gupta: So sometimes we want.
      
      281
      00:30:47.970 --> 00:30:48.500
      Dexter Horthy: Shit.
      
      282
      00:30:49.940 --> 00:30:55.999
      Vaibhav Gupta: But we don't want it to do reasoning as a data field. I don't want to deal with that. I just wanted to like output something.
      
      283
      00:30:56.700 --> 00:30:58.800
      Vaibhav Gupta: and I want to show you what happens here.
      
      284
      00:31:00.470 --> 00:31:06.900
      Vaibhav Gupta: If this works exam.
      
      285
      00:31:06.900 --> 00:31:18.719
      Dexter Horthy: Okay, so this is getting into like, how do we? How do we? This is a great leeway. This is like, how do we get the model to output busted Json in a way that like actually helps it get better. Answers.
      
      286
      00:31:23.560 --> 00:31:26.740
      Dexter Horthy: like comments in Json are technically not valid.
      
      287
      00:31:28.270 --> 00:31:31.879
      Vaibhav Gupta: Let's see if I can force it to do this. I have to actually read the prompt and see what it's doing
      
      288
      00:31:36.020 --> 00:31:37.210
      Vaibhav Gupta: views.
      
      289
      00:31:40.110 --> 00:31:41.240
      Dexter Horthy: As.
      
      290
      00:31:42.370 --> 00:32:11.450
      Vaibhav Gupta: If if not, if speaker is ambiguous, list relevant comments the help, narrow help a narrow down toggle
      
      291
      00:32:12.700 --> 00:32:14.572
      Vaibhav Gupta: to help narrow down.
      
      292
      00:32:15.600 --> 00:32:16.860
      Vaibhav Gupta: No speaker
      
      293
      00:32:25.890 --> 00:32:27.320
      Vaibhav Gupta: use 1st
      
      294
      00:32:31.240 --> 00:32:31.910
      Vaibhav Gupta: cool.
      
      295
      00:32:34.940 --> 00:32:37.180
      Vaibhav Gupta: and we'll go run this and see what the model does.
      
      296
      00:32:38.130 --> 00:32:41.199
      Vaibhav Gupta: Okay, I can't get to do it. Let me try and put this out.
      
      297
      00:32:44.860 --> 00:32:47.659
      Vaibhav Gupta: This is like the weirdest trick that I've learned, and.
      
      298
      00:32:56.490 --> 00:33:00.680
      Dexter Horthy: So, not directly in the generated output format, but just in the prompt.
      
      299
      00:33:01.820 --> 00:33:03.130
      Vaibhav Gupta: And the XM.
      
      300
      00:33:04.100 --> 00:33:12.450
      Vaibhav Gupta: Use fresh and had, and excellent.
      
      301
      00:33:14.120 --> 00:33:14.790
      Dexter Horthy: Okay.
      
      302
      00:33:15.000 --> 00:33:18.040
      Dexter Horthy: So you always tell me not to use a few shot prompting.
      
      303
      00:33:18.690 --> 00:33:19.600
      Vaibhav Gupta: I do?
      
      304
      00:33:21.250 --> 00:33:29.120
      Dexter Horthy: Because this is more about the structure of the response, not about the actual, like learning from examples, basically.
      
      305
      00:33:29.120 --> 00:33:30.120
      Vaibhav Gupta: Exactly.
      
      306
      00:33:30.610 --> 00:33:35.510
      Vaibhav Gupta: So let's see if I can get the model to output this. And sometimes I can't. Sometimes the model doesn't really listen
      
      307
      00:33:36.027 --> 00:33:44.330
      Vaibhav Gupta: and just dump that info as another field. So let's do another last thing prefix equals answer. With
      
      308
      00:33:44.630 --> 00:33:48.409
      Vaibhav Gupta: this I noticed Openai has been doing this.
      
      309
      00:33:49.250 --> 00:33:58.119
      Vaibhav Gupta: Oh, where like, I think, for whatever reason, whenever you use the word Json, they trigger something special in the prompt that goes to like some other model or something.
      
      310
      00:33:58.120 --> 00:34:01.390
      Dexter Horthy: So, or like secretly turns on.
      
      311
      00:34:01.390 --> 00:34:03.859
      Vaibhav Gupta: There you go. Yes, exactly.
      
      312
      00:34:06.110 --> 00:34:08.535
      Vaibhav Gupta: And now the models actually
      
      313
      00:34:09.874 --> 00:34:13.775
      Vaibhav Gupta: writing some more comments. But it's right in the comments after
      
      314
      00:34:14.320 --> 00:34:21.739
      Vaibhav Gupta: If list relevant facts helping out on Speaker before the speaker fields see you but be a little.
      
      315
      00:34:21.739 --> 00:34:23.969
      Dexter Horthy: Reasoning before the output.
      
      316
      00:34:24.159 --> 00:34:24.729
      Vaibhav Gupta: Yeah.
      
      317
      00:34:26.265 --> 00:34:33.150
      sahil: Question. So the reason to do this is to save the tokens on item clue. Every single.
      
      318
      00:34:33.159 --> 00:34:33.689
      Vaibhav Gupta: Oh, okay.
      
      319
      00:34:33.889 --> 00:34:34.690
      sahil: It is.
      
      320
      00:34:34.690 --> 00:34:43.710
      Vaibhav Gupta: It's not. It's not always about that. It's just like the model might just. It's just another tool in your toolbox for how you can get the model to output. What you want
      
      321
      00:34:44.260 --> 00:34:46.130
      Vaibhav Gupta: clues is one way to do it.
      
      322
      00:34:47.620 --> 00:35:02.900
      Dexter Horthy: And you can also do the thing we do. It's like, put the reasoning at the top and then dump the Json, and it sounds like this is just like, okay, if we want really targeted reasoning on each field. And maybe like, this is way more token efficient than having it output a bunch of extra. Json.
      
      323
      00:35:03.910 --> 00:35:15.300
      Vaibhav Gupta: Exactly, and you'll notice that you saw me iterate a little bit on this prompt over here, like I did a couple of things to go do this. But this goes into the very next tip that I want to really talk about.
      
      324
      00:35:15.410 --> 00:35:17.839
      Vaibhav Gupta: which is one
      
      325
      00:35:18.430 --> 00:35:26.989
      Vaibhav Gupta: it's called Rtfp. For those of you that don't know. Rtfm, it means read the fucking manual. Rtfp means read the fucking prompt.
      
      326
      00:35:27.397 --> 00:35:41.500
      Vaibhav Gupta: And I say that with a lot of love, because most people don't actually read the prompt. And you saw what I did when this didn't work over here. I just read the prompt I was like, oh, if I go back to the add description mechanism, let me give you a little bit more of a
      
      327
      00:35:41.850 --> 00:35:43.699
      Vaibhav Gupta: description of why I didn't like this.
      
      328
      00:35:45.120 --> 00:35:51.210
      Vaibhav Gupta: When I go read this, I'm like, oh, this thing over here. Maybe it's getting confused by the double comments.
      
      329
      00:35:52.690 --> 00:36:03.010
      Vaibhav Gupta: and you can see how that might be confusing to the model. So since I'm using comments like nested comments and comments, I'm like, okay, let me just try and simplify this problem for the model
      
      330
      00:36:03.340 --> 00:36:07.850
      Vaibhav Gupta: and give it that in a place where it can't be confused.
      
      331
      00:36:07.990 --> 00:36:11.340
      Vaibhav Gupta: and that was the intuition that I had out here.
      
      332
      00:36:12.834 --> 00:36:20.980
      Vaibhav Gupta: So it really just boils on to reading the prompt, because if we can read the prompt, then we can see what the model might be doing. And of course we can never actually know what's actually happening.
      
      333
      00:36:21.770 --> 00:36:28.940
      Vaibhav Gupta: but it allows us to actually know what it allows us to iterate a little bit faster, and then we can say, Oh, that isn't working. Let me go fix that.
      
      334
      00:36:29.080 --> 00:36:51.790
      Vaibhav Gupta: There's a question about why not use few shot prompting? There's a couple of reasons. Typically the way to have done few shot. Prompting in this example would have been me to actually go and write an example and then write out the answer. But that's not what I wanted. I just wanted the model to understand that it has the ability to go do this. It has the ability to list out facts before it actually spits out the speaker field.
      
      335
      00:36:52.160 --> 00:36:56.449
      Vaibhav Gupta: So I just wanted to give it the structure. So it understands the thing it has to mimic.
      
      336
      00:36:56.640 --> 00:36:58.450
      Vaibhav Gupta: I don't. It's not the contact.
      
      337
      00:36:58.970 --> 00:37:00.490
      Dexter Horthy: Go ahead, Dexter.
      
      338
      00:37:00.690 --> 00:37:23.570
      Dexter Horthy: And all this is again, is like, Okay, cool, like, yeah. Probably just outputting. Json is good enough. Outputting. Reasoning. 1st is a little bit better. Having reasoning in your Json. Fields is probably a little bit better. But if you're running this kind of thing a hundred 1,000 times a day, then a tiny half a percent improvement, either in efficiency or in speed or in token efficiency or in accuracy.
      
      339
      00:37:23.570 --> 00:37:34.359
      Dexter Horthy: is massively valuable. And this is what we talk about every week on this show like, how do you? How do you unlock those like near the top of the accuracy range? How do you push things even further.
      
      340
      00:37:34.720 --> 00:37:36.750
      Vaibhav Gupta: Yeah, how do you get another half a percent?
      
      341
      00:37:37.150 --> 00:37:41.709
      Vaibhav Gupta: And this isn't. Again, remember, this isn't say that this technique will work always.
      
      342
      00:37:42.270 --> 00:37:51.590
      Vaibhav Gupta: But it is another technique that you have available to yourself, just like we use this other technique to not spit out the entire dialog, but rather only spit out the index.
      
      343
      00:37:52.500 --> 00:37:59.219
      Vaibhav Gupta: And we use this other technique to say, Oh, dialogue index is actually a lot more tokens. Let's use purely the word index
      
      344
      00:37:59.420 --> 00:38:03.289
      Vaibhav Gupta: instead. So it spits out. The output. Tokens are way less.
      
      345
      00:38:03.290 --> 00:38:07.980
      Vaibhav Gupta: Hi, Chris, it's small things that can make a difference. And if I actually were to look at this.
      
      346
      00:38:08.160 --> 00:38:12.799
      Vaibhav Gupta: my punch actually says index itself, where to go.
      
      347
      00:38:12.800 --> 00:38:13.430
      Dexter Horthy: And.
      
      348
      00:38:13.430 --> 00:38:27.209
      Vaibhav Gupta: Index is probably wrong. I should actually probably use like index, because this is just a more popular token that the model will have understandings of, or rather than idx, even though idx is a single token. It's just more commonly understood.
      
      349
      00:38:27.970 --> 00:38:29.320
      Dexter Horthy: Existing processes.
      
      350
      00:38:30.306 --> 00:38:32.280
      Vaibhav Gupta: Cool, so.
      
      351
      00:38:32.280 --> 00:38:57.380
      sahil: Question, quick question. So we do this actually hundreds and thousands of times a day where we put out reasoning. And we use the reasoning as for another model, so is there a way to achieve or make it a bit more efficient? So we literally spit out clues, and these are at least a long sentence.
      
      352
      00:38:58.820 --> 00:39:02.800
      sahil: So any any tips or tricks do.
      
      353
      00:39:03.108 --> 00:39:10.200
      Vaibhav Gupta: If you really wanted, if you really wanted like if you really wanted that, I would actually put your reasoning afterwards
      
      354
      00:39:10.610 --> 00:39:12.060
      Vaibhav Gupta: like assessment.
      
      355
      00:39:14.540 --> 00:39:26.120
      Vaibhav Gupta: So if you want to do an eval thing right over here, description, final assessment of the speaker.
      
      356
      00:39:26.440 --> 00:39:35.159
      Vaibhav Gupta: Given any clues prior clues in comments, I received this
      
      357
      00:39:38.210 --> 00:39:44.669
      Vaibhav Gupta: and just like, let the model spit it out. And now you can use assessment as a thing. But now you'll see that assessment is actually kind of big.
      
      358
      00:39:44.850 --> 00:39:47.350
      Vaibhav Gupta: So what I'll do is like use phrases
      
      359
      00:39:52.283 --> 00:39:58.100
      Vaibhav Gupta: not complete sentences. And then I would also add into here
      
      360
      00:40:01.260 --> 00:40:02.150
      Vaibhav Gupta: assessment.
      
      361
      00:40:03.720 --> 00:40:11.949
      Vaibhav Gupta: So now I'll notice over here what it's doing, and it will just spit something out, and I would probably have to tweak this model. So sometimes Gt. 4 is not very good. So let me try. Anthropic.
      
      362
      00:40:13.510 --> 00:40:15.320
      Vaibhav Gupta: Is that the right model? We'll find out.
      
      363
      00:40:15.910 --> 00:40:17.390
      Vaibhav Gupta: Oh, that is not the right model.
      
      364
      00:40:18.290 --> 00:40:20.210
      Dexter Horthy: Dude, I think it's 1020.
      
      365
      00:40:23.440 --> 00:40:25.040
      Dexter Horthy: 2024, 1020.
      
      366
      00:40:25.670 --> 00:40:27.050
      Vaibhav Gupta: Custom, sonic.
      
      367
      00:40:27.640 --> 00:40:28.340
      Dexter Horthy: There you go!
      
      368
      00:40:29.880 --> 00:40:34.320
      Vaibhav Gupta: Oh, I don't have an Api key! One second. I will not be sharing my Api key this time around.
      
      369
      00:40:35.050 --> 00:40:38.260
      Dexter Horthy: Oh, that's why I come here every week.
      
      370
      00:40:38.390 --> 00:40:41.000
      Dexter Horthy: It's because you always you always leak at least one key.
      
      371
      00:40:41.400 --> 00:40:43.210
      Vaibhav Gupta: Also forget to deactivate it.
      
      372
      00:40:47.090 --> 00:40:50.010
      Vaibhav Gupta: Okay, let me.
      
      373
      00:40:53.290 --> 00:40:57.440
      Dexter Horthy: Yeah, and just answering it while he's doing that, answering the question on the thread.
      
      374
      00:40:58.544 --> 00:41:04.736
      Dexter Horthy: why not use few shot prompting. We talked about this a little bit. But it's basically
      
      375
      00:41:05.340 --> 00:41:11.930
      Dexter Horthy: the content of the examples tends to greatly steer the model's response.
      
      376
      00:41:12.290 --> 00:41:21.450
      Dexter Horthy: And like you can get, you can get the right structural results without actually putting content in your examples.
      
      377
      00:41:22.200 --> 00:41:23.030
      Vaibhav Gupta: Yes.
      
      378
      00:41:23.719 --> 00:41:37.190
      Vaibhav Gupta: so there we go. So now you can see over here when I switch this Claude, I actually get really nice things where it's assessment comes with this. And now you could plug this into your evals. We got a way less tokens out here. It's way. It's way shorter
      
      379
      00:41:38.360 --> 00:41:56.589
      Vaibhav Gupta: because we're not using complete sentences. So if you really care about evals and want to like you want to store the data anyway, go do that. But honestly, if you're up to me, I wouldn't do any of this Eval stuff online, I would have a separate process that pulls all my data down and runs a separate Eval, including the assessment for each of these segments off the raw data itself
      
      380
      00:41:57.240 --> 00:42:08.659
      Vaibhav Gupta: and just run a completely separate process. It's going to be way cheaper way faster, because don't add more latency to a pipeline that has this. Each of these things that you're generating here is latency. So a very latency, sensitive pipeline generally for speech to text.
      
      381
      00:42:10.240 --> 00:42:10.970
      Dexter Horthy: Cool.
      
      382
      00:42:12.075 --> 00:42:23.119
      Vaibhav Gupta: Cool. Let's talk about so at this point we've covered labels. Don't use uids. Don't use you urls use like indexes whenever possible and remap them programmatically to the right thing.
      
      383
      00:42:23.370 --> 00:42:33.389
      Vaibhav Gupta: We've talked about. Diarization don't emit the full transcript. Have the again, have the index, have the model represent something that is way better than the full transcript. In this case an index of the transcript
      
      384
      00:42:33.810 --> 00:42:38.110
      Vaibhav Gupta: we've talked about using inline comments to guide reasoning of sorts.
      
      385
      00:42:38.350 --> 00:42:53.019
      Vaibhav Gupta: We've talked about Re. Rtfd. Reading the prompt read it always, especially when you get stuck instead of trying to keep prompting more. Just keep reading it. We've talked about few shot prompting with structure, not with actual content, and how we can leverage that along the way.
      
      386
      00:42:53.770 --> 00:42:59.269
      Vaibhav Gupta: And I think the next thing I want to talk about is something that we've mentioned a few times. But it's all about Cogen.
      
      387
      00:42:59.990 --> 00:43:06.370
      Vaibhav Gupta: So I'm going to go ahead and pull up a random new file.
      
      388
      00:43:06.720 --> 00:43:19.140
      Anubhav: Hey, web Anupav! Here, before you move forward, I in my mind I'm still confused about using this technique where you somehow use Ginger to get an index on that array.
      
      389
      00:43:20.230 --> 00:43:22.640
      Vaibhav Gupta: I, yeah, good.
      
      390
      00:43:22.850 --> 00:43:29.829
      Anubhav: Versus using symbol tuning thing. So when to use what.
      
      391
      00:43:30.255 --> 00:43:30.680
      Vaibhav Gupta: Okay.
      
      392
      00:43:30.680 --> 00:43:35.760
      Vaibhav Gupta: okay, so just for context, let me just pull up a symbol to example. So then I, we can just talk about it.
      
      393
      00:43:39.840 --> 00:43:40.959
      Dexter Horthy: And it was the second or 3.rd
      
      394
      00:43:40.960 --> 00:43:42.890
      Vaibhav Gupta: Services. That's like the one
      
      395
      00:43:43.561 --> 00:43:51.359
      Vaibhav Gupta: I have symbol tuning right here. So the idea of symbol tuning is I want to do a classification example. I guess I'll do this
      
      396
      00:43:52.430 --> 00:43:55.900
      Vaibhav Gupta: symbol doing a
      
      397
      00:44:08.197 --> 00:44:17.240
      Vaibhav Gupta: I have a classification prompt instead of actually classifying the prompt. I want them all to spit out one of these categories, and I have a couple of different ways. I can go do this. Oh, that's interesting.
      
      398
      00:44:18.680 --> 00:44:22.739
      Vaibhav Gupta: I have a couple of different ways that I can go do this. But one of the ways is like.
      
      399
      00:44:23.400 --> 00:44:25.660
      Vaibhav Gupta: instead of the model actually spitting out
      
      400
      00:44:26.495 --> 00:44:35.540
      Vaibhav Gupta: all of my classes, I can. And instead of actually writing like the word refund in the prompt, I can write just the symbol, k. 1.
      
      401
      00:44:35.980 --> 00:44:37.750
      Vaibhav Gupta: And when the model runs this
      
      402
      00:44:37.950 --> 00:44:52.139
      Vaibhav Gupta: it will spit out K. 4, which then gets remapped to account issue for me automatically. The benefit of this approach is the model. Again, it's same. It's the exact same thing as the Youtube URL thing, where the model, when it sees the word account issue.
      
      403
      00:44:52.270 --> 00:45:02.139
      Vaibhav Gupta: it associates these tokens with something semantically meaningful. And what I want to do is my meaning of an account issue is actually encoded in my description way. Better than that.
      
      404
      00:45:02.140 --> 00:45:03.360
      Dexter Horthy: You want to say
      
      405
      00:45:03.610 --> 00:45:14.489
      Dexter Horthy: 0 attention on the label name, because that's for the coders and the program that's consuming this all attention on the description, so that I can control exactly what the Lm. Is going to output.
      
      406
      00:45:15.060 --> 00:45:21.420
      Vaibhav Gupta: Exactly exactly. It's about reducing the number of variability in the problem, Dexter said it beautifully.
      
      407
      00:45:21.930 --> 00:45:28.019
      Vaibhav Gupta: and symbol tuning is a technique. Lets me do this, the thing that we're talking about with diarization, where we output
      
      408
      00:45:28.633 --> 00:45:40.319
      Vaibhav Gupta: where we actually output like the actual index here, that's basically the same thing instead of the model outputting the actual text of the line, it's outputting the index of the line in the conversation.
      
      409
      00:45:40.660 --> 00:45:49.800
      Vaibhav Gupta: and instead of letting the model infer the index. Because I could do that. I don't actually have to write this. I could just let the model infer the index by writing something like this instead.
      
      410
      00:45:51.090 --> 00:45:52.950
      Dexter Horthy: Just in the model break. Yeah.
      
      411
      00:45:52.950 --> 00:45:58.019
      Vaibhav Gupta: Model could count. But why make the life harder for the model like this?
      
      412
      00:45:58.020 --> 00:46:04.910
      Dexter Horthy: Yeah. Now you're asking the model to count shit. Are you kidding me? That's terrifying. It's like, it's like, you know, when you do these coding agents, and you have, like
      
      413
      00:46:05.070 --> 00:46:11.650
      Dexter Horthy: no line numbers in the file versus every time you give it to the model, give it line numbers, and suddenly it can do these edits way. Better, right?
      
      414
      00:46:12.060 --> 00:46:20.929
      Vaibhav Gupta: Exactly, and this goes back to Rtfp. If I read this prompt even as a human. I know exactly what index this is without having to spend any time about it.
      
      415
      00:46:21.690 --> 00:46:26.039
      Vaibhav Gupta: But if I don't have these lines in there that becomes a lot harder for me to go, do.
      
      416
      00:46:26.520 --> 00:46:44.909
      Vaibhav Gupta: And I think it's small things like this that actually, dramatically change the quality of your outputs in a way that I think can make a huge difference. So I hope. I related the questions across the board, for the one of how simple tuning relates to diarization and the examples.
      
      417
      00:46:45.750 --> 00:47:15.680
      Dexter Horthy: And I. We won't go into this today, I think. But, like again, take all the advice from the Evals chapter and like, Don't go just applying all this stuff, willy, nilly like, get a real set. Understand what how your performance is today. Try changing these small things, you know whether it's like, Oh, I found a bug from production. Let me drop it in as a test case, and just change the prompt until I fix this one without breaking all the other ones, or even having a bigger Eval set, which is like, Hey, our accuracy is 84%. And if I make this change and run the exact same data through the pipeline. Now, it's 88%.
      
      418
      00:47:16.420 --> 00:47:18.610
      Vaibhav Gupta: Exactly exactly.
      
      419
      00:47:19.940 --> 00:47:20.570
      Vaibhav Gupta: Let's.
      
      420
      00:47:20.570 --> 00:47:21.000
      Dexter Horthy: Cool.
      
      421
      00:47:21.000 --> 00:47:25.330
      Vaibhav Gupta: Let's talk with the last part. Cogen. This is something we showed a couple of times, and this is kind of
      
      422
      00:47:25.790 --> 00:47:27.650
      Vaibhav Gupta: ex-related.
      
      423
      00:47:28.250 --> 00:47:45.929
      Dexter Horthy: Yeah, this directly leads from the other one, because it's again, it's like, how do we get the model to create invalid Json for good like, how? How can? By getting the model to create broken Json, you can actually get way. Better performance. And we'll talk about like, why, that works by looking like under the hood at like samplers and stuff right.
      
      424
      00:47:46.380 --> 00:47:48.290
      Vaibhav Gupta: Yeah, let's do that. That's actually a good idea.
      
      425
      00:47:48.630 --> 00:47:49.650
      Vaibhav Gupta: So in this case.
      
      426
      00:47:49.650 --> 00:47:50.480
      Dexter Horthy: I want to.
      
      427
      00:47:50.480 --> 00:47:55.809
      Vaibhav Gupta: Generate some code. And I'll say, a binary search tree
      
      428
      00:47:56.020 --> 00:48:04.820
      Vaibhav Gupta: with actually, no, let's do this. A sorting algorithm with merge sort.
      
      429
      00:48:05.260 --> 00:48:10.019
      Vaibhav Gupta: Alright cool. That's record that's redundant. So let's do this. Firstly.
      
      430
      00:48:11.540 --> 00:48:16.179
      Vaibhav Gupta: and it's gonna output this. And again, if I have a chat app, this is excellent.
      
      431
      00:48:17.680 --> 00:48:29.859
      Vaibhav Gupta: This is really really excellent. I could show this to the user. They'll be pretty happy, and we'll see the quality of the code right here. It looks pretty good. It has some comments and stuff in it. It looks generally useful.
      
      432
      00:48:30.490 --> 00:48:31.539
      Vaibhav Gupta: but the minute.
      
      433
      00:48:31.540 --> 00:48:44.149
      Dexter Horthy: This is the way models want to write code, by the way, like this is, if you if you just want to get the very best code performance. Let it write it between Markdown back ticks, because that is what is the majority present in the training set.
      
      434
      00:48:44.490 --> 00:48:45.060
      Vaibhav Gupta: Yeah.
      
      435
      00:48:45.170 --> 00:48:54.929
      Vaibhav Gupta: Now, I'm gonna change this to actually return a data model. Because, hey, I want the code so I can go find it. I don't do some parsing. I want to render it just the code part without all this prefix. Or maybe I want to go run it and go do something.
      
      436
      00:48:54.930 --> 00:49:00.789
      Dexter Horthy: You don't want to have to write code to strip out that like python back ticks thing because you're just going to turn around and run it. Maybe.
      
      437
      00:49:01.310 --> 00:49:05.699
      Vaibhav Gupta: And now we got this, and I don't actually know the quality of this code.
      
      438
      00:49:06.130 --> 00:49:22.800
      Vaibhav Gupta: but we'll see. All I do know is it did output a lot of things, and I want everyone to know something very, very important here. This is actually what the model output. This is raw. I just copied. Directly the string the model came out with. If I go back to the Tokenizer I'll show you. I want to show everyone what this means.
      
      439
      00:49:24.500 --> 00:49:26.120
      Vaibhav Gupta: We can see what it did.
      
      440
      00:49:26.600 --> 00:49:29.239
      Dexter Horthy: Yo slash and n are 2 different tokens.
      
      441
      00:49:29.560 --> 00:49:31.180
      Vaibhav Gupta: Yeah, exactly. So it's actually.
      
      442
      00:49:31.180 --> 00:49:32.250
      Dexter Horthy: That's crazy.
      
      443
      00:49:32.250 --> 00:49:41.360
      Vaibhav Gupta: It's outputting a bunch of space characters. It's it's not actually outputting code. It's outputting something slightly different. It's something that looks like code.
      
      444
      00:49:41.700 --> 00:49:47.359
      Dexter Horthy: Will you? Sorry? Can I screenshot that? And then can you drop the other output into the tokenizer as well.
      
      445
      00:49:48.360 --> 00:49:49.030
      Vaibhav Gupta: Yeah. Why not?
      
      446
      00:49:49.030 --> 00:49:51.060
      Dexter Horthy: Back and let me get a screenshot real quick.
      
      447
      00:49:52.910 --> 00:49:54.870
      Vaibhav Gupta: Yeah, I'll put side by side. How about that?
      
      448
      00:49:55.180 --> 00:49:59.260
      Dexter Horthy: Okay, yeah, because I think this is really important.
      
      449
      00:50:01.780 --> 00:50:02.400
      Vaibhav Gupta: Okay.
      
      450
      00:50:09.070 --> 00:50:14.369
      Dexter Horthy: So if you get rid of the back ticks and the actual like, preamble and stuff, how do the token.
      
      451
      00:50:14.370 --> 00:50:23.309
      Vaibhav Gupta: No, I'll I'll leave that in there, actually. Because I think it's important. And this one has like a Java example as well. So why not get rid of the Java example.
      
      452
      00:50:23.840 --> 00:50:24.500
      Dexter Horthy: Yeah.
      
      453
      00:50:24.680 --> 00:50:26.857
      Vaibhav Gupta: Just to like, keep it in.
      
      454
      00:50:29.100 --> 00:50:34.660
      Vaibhav Gupta: There's something in here cool.
      
      455
      00:50:34.770 --> 00:50:38.229
      Vaibhav Gupta: and this seems to have a print example as well. So we leave that in there.
      
      456
      00:50:38.630 --> 00:50:54.549
      Vaibhav Gupta: What we'll notice here is not. It's not really about the token counts or anything else. What's really important here is like the quality of the code that's being generated. 1st thing that we notice upfront is recursively sort both halves. So this comes out. And then, if we go look at this all these backslash ends
      
      457
      00:50:54.940 --> 00:51:01.370
      Vaibhav Gupta: are actually having to be forcefully generated by the model, to be correctly syntactical. Json out of here.
      
      458
      00:51:02.060 --> 00:51:05.690
      Dexter Horthy: Because you can't have new lines in Json. You have to have escaped new lines.
      
      459
      00:51:05.940 --> 00:51:11.489
      Vaibhav Gupta: Exactly, instead of letting the model just do escape new lines. So what if we just told the model to go do that instead?
      
      460
      00:51:11.740 --> 00:51:26.470
      Vaibhav Gupta: What we'll find is code description. Use, use triple use back, take use triple backticks, the format code, code.
      
      461
      00:51:26.930 --> 00:51:28.010
      Vaibhav Gupta: python.
      
      462
      00:51:30.680 --> 00:51:34.639
      Vaibhav Gupta: and let's go read the Prompt. Let's see what the prompt looks like. This is what the prompt looks like.
      
      463
      00:51:35.070 --> 00:51:37.020
      Vaibhav Gupta: Use triple backfix to read the prompt
      
      464
      00:51:39.600 --> 00:51:42.870
      Vaibhav Gupta: And now, when I go run this, what I get
      
      465
      00:51:42.980 --> 00:51:46.589
      Vaibhav Gupta: is the model output code exactly how I was outputting before.
      
      466
      00:51:48.320 --> 00:51:51.280
      Vaibhav Gupta: but in a way that still allows me to do structured promptly.
      
      467
      00:51:51.900 --> 00:52:12.870
      Dexter Horthy: So this is not valid, Json, and like the subtle thing here is like. And this is kind of like, I think we're having a conversation yesterday about like one of the cool things you can do with Bamel, and why, having a parser that is separate from the that is outside of the model itself is really powerful is because you can let the model use regular new lines and its output, and then turn them back into J, like regular, like Json, that works.
      
      468
      00:52:14.330 --> 00:52:19.900
      Vaibhav Gupta: Yes, so now let's go. Do this. Now, I want to make this as a lesson plan
      
      469
      00:52:20.140 --> 00:52:24.469
      Vaibhav Gupta: for the following, input as a lesson with diffs.
      
      470
      00:52:26.250 --> 00:52:30.260
      Vaibhav Gupta: So now, what I'm going to do is I'm going to output an array of code snippets.
      
      471
      00:52:30.700 --> 00:52:31.970
      Vaibhav Gupta: Not one
      
      472
      00:52:32.970 --> 00:52:39.719
      Vaibhav Gupta: but multiple arrays. And then I'm gonna say, make a plan. To for to go do this example.
      
      473
      00:52:41.970 --> 00:52:46.170
      Vaibhav Gupta: Section one. Blah blah blah section 2, blah blah blah blah
      
      474
      00:52:49.180 --> 00:52:56.280
      Vaibhav Gupta: cool. And again, what do you think? Few shop the example of using comments as guiding principles? We're gonna do the same thing here.
      
      475
      00:52:57.200 --> 00:52:59.609
      Vaibhav Gupta: and then we'll add a little title here, string
      
      476
      00:53:02.270 --> 00:53:10.530
      Dexter Horthy: This is funny. This is what I actually did for a workshop a couple weeks ago, was we had said, Hey, here's the final product, output it as sections in a lesson plan.
      
      477
      00:53:12.130 --> 00:53:13.819
      Vaibhav Gupta: So now we're gonna do the same thing.
      
      478
      00:53:15.670 --> 00:53:18.080
      Vaibhav Gupta: And now what the model is, I'm fixing this bug.
      
      479
      00:53:18.390 --> 00:53:23.029
      Dexter Horthy: I mean, this is cool. But why, why would you want to do it this way? Why would you want to do this?
      
      480
      00:53:23.030 --> 00:53:23.880
      Dexter Horthy: It's like us.
      
      481
      00:53:24.140 --> 00:53:34.370
      Vaibhav Gupta: I'll show you the output, because I think the output will make it more clear. So the 1st thing is, I wanted to build a lesson plan so I did reasoning for like what lesson plan I wanted to go do. So it said, what we're gonna do this.
      
      482
      00:53:34.540 --> 00:53:36.580
      Vaibhav Gupta: then it's going to actually output the code
      
      483
      00:53:36.920 --> 00:53:47.039
      Vaibhav Gupta: and create a merge function that combines 2 sort of arrays. Great create a basic merge sort function with recursion. So it's actually incrementing it. Now you can imagine that I walk someone through the code
      
      484
      00:53:47.360 --> 00:53:48.620
      Vaibhav Gupta: one by one.
      
      485
      00:53:49.850 --> 00:54:03.160
      Vaibhav Gupta: right. And now it's intending with array, splitting recursive calls. So now it's incrementally going to do this. Now I can build a ui on top of this. That literally has step one step, 2, step 3, and teach someone merge sort with this benefit along the way.
      
      486
      00:54:04.580 --> 00:54:10.440
      Vaibhav Gupta: right and along the whole time. If I get rid of this section I will. I will literally just comment this part out.
      
      487
      00:54:11.750 --> 00:54:15.319
      Vaibhav Gupta: I'll show you how much harder it becomes for the model to actually generate this
      
      488
      00:54:19.140 --> 00:54:24.490
      Vaibhav Gupta: like this is now like becoming significantly harder
      
      489
      00:54:24.720 --> 00:54:29.500
      Vaibhav Gupta: for the model to actually keep track of its own code, because even as a developer
      
      490
      00:54:29.750 --> 00:54:43.019
      Vaibhav Gupta: this would be very, very hard for me to even unread and understand this and most of the training data and the models Codegen doesn't actually have backslash ends as this. It has it as the actual backslash end.
      
      491
      00:54:43.250 --> 00:54:52.550
      Vaibhav Gupta: So code quality that you're getting is going to be way worse. So when we go to like a harder problem, let's go into a harder problem, because merge sort is something that we all know, like even the basic models can go do.
      
      492
      00:54:54.820 --> 00:54:58.160
      Vaibhav Gupta: Create a what is it? What's a harder problem next, sir?
      
      493
      00:54:59.129 --> 00:55:04.069
      Dexter Horthy: Kubernetes operator to spin up Rds. Instances in Golang.
      
      494
      00:55:08.830 --> 00:55:10.760
      Vaibhav Gupta: To spin up our.
      
      495
      00:55:10.760 --> 00:55:14.049
      Dexter Horthy: Spin up yeah instances and go lang.
      
      496
      00:55:15.080 --> 00:55:16.789
      Vaibhav Gupta: I have no idea.
      
      497
      00:55:18.680 --> 00:55:22.449
      Vaibhav Gupta: I have no idea what half those words mean, because sadly, I work in algorithms land.
      
      498
      00:55:23.300 --> 00:55:25.390
      Vaibhav Gupta: and we're seeing what the model is. So I want you.
      
      499
      00:55:25.390 --> 00:55:26.620
      Dexter Horthy: Oh, it made a diff.
      
      500
      00:55:26.960 --> 00:55:28.020
      Dexter Horthy: Yes.
      
      501
      00:55:28.020 --> 00:55:29.360
      Vaibhav Gupta: Maldo's made a death.
      
      502
      00:55:29.510 --> 00:55:41.060
      Vaibhav Gupta: I also want us to notice a couple other things. The model actually, intuitively just put out back tick new lines. Anyway, it actually was like, you know, what I am not going to put out backslash ends. I'm just going to spit out this.
      
      503
      00:55:41.230 --> 00:55:43.789
      Vaibhav Gupta: So model intuitively did this for us
      
      504
      00:55:44.930 --> 00:55:50.049
      Vaibhav Gupta: without us even having to prompt at that. And that just goes to show that the model's intuitive behavior
      
      505
      00:55:50.470 --> 00:55:57.399
      Vaibhav Gupta: is not to spit out, escaped Json, and the reason it probably did this
      
      506
      00:55:57.670 --> 00:56:08.230
      Vaibhav Gupta: is because go is just a lot more technical than python or typescript and other things. So the minute it got to like a hard mode problem. It did the most basic things for itself.
      
      507
      00:56:09.290 --> 00:56:16.300
      Dexter Horthy: Yeah, you wanna pop back to the whiteboard for really quick and just highlight. I I wanna highlight this sampling part of this
      
      508
      00:56:17.900 --> 00:56:19.108
      Vaibhav Gupta: So you have it too.
      
      509
      00:56:19.350 --> 00:56:20.200
      Dexter Horthy: Yeah. Yeah.
      
      510
      00:56:24.300 --> 00:56:24.790
      Vaibhav Gupta: There you go!
      
      511
      00:56:24.790 --> 00:56:38.520
      Dexter Horthy: So, okay, so you got that up scroll down a little bit. So basically like, if if you know how samplers work, essentially, you have at any given point. You have, you know, the models writing code, and it's writing, like, you know, code
      
      512
      00:56:38.690 --> 00:56:44.490
      Dexter Horthy: import OS, and then at any given point, it's it's we're at. Let's say we're right here.
      
      513
      00:56:44.760 --> 00:56:58.430
      Dexter Horthy: and we're generating like. Then we're asking what's the next token? At this moment there is, you know, and a distribution of what the next token is going to be right. And in this case it's almost always going to be like
      
      514
      00:56:58.530 --> 00:57:08.779
      Dexter Horthy: new line kind of classic new line. And then there's going to be a long tail of other characters. That might be next right? You might have, you know, semicolon here.
      
      515
      00:57:10.260 --> 00:57:29.840
      Dexter Horthy: because maybe some code has like import OS semicolon. And then another import. Maybe if it's red code serialized in Json, maybe there is a backslash here which is going to lead it to correctly type the slash N, and maybe there's some other characters here defined by your temperature, right of like different probabilities of that. That's the next token?
      
      516
      00:57:30.270 --> 00:57:31.310
      Dexter Horthy: Does it make sense.
      
      517
      00:57:31.830 --> 00:57:32.460
      Vaibhav Gupta: Yup!
      
      518
      00:57:33.040 --> 00:57:47.999
      Dexter Horthy: So when you put on strict mode or strict Json mode, and even in some of the more like old school function calling modes, they're starting to enforce this. Basically that is going to when the model gets to its like time to do the correct output.
      
      519
      00:57:48.030 --> 00:58:10.569
      Dexter Horthy: It's just going to X out anything that would break the Json schema, which means that a new line is not a valid character, because a new line is not valid, Json, and this is why, when people say, like, you know, using strict mode reduces the accuracy of your outputs, it's because now you're removing the big one, and you have a very, very like
      
      520
      00:58:10.730 --> 00:58:30.700
      Dexter Horthy: tight distribution of the other things. Now these probabilities get balanced out, and you have a bunch of things that are like probably next, but like not clear. And so you're likely to get weird janky code with like semicolons in it, instead of backslashes, or even like invalid syntax, because you're not letting the model write code in the way that it's been trained to write code.
      
      521
      00:58:31.550 --> 00:58:38.520
      Vaibhav Gupta: Yeah. And this applies not just for Cogen, but applies to any domain where anytime you're having the model not pick its best token.
      
      522
      00:58:38.920 --> 00:58:44.290
      Vaibhav Gupta: You're basically telling the model like you know better than model, which may be true in some scenarios. I want to articulate that.
      
      523
      00:58:44.910 --> 00:58:50.219
      Vaibhav Gupta: But most of the time in machine learning. What we've learned is, let the model do what it does best
      
      524
      00:58:50.350 --> 00:59:05.340
      Vaibhav Gupta: and just let it output the best token. And in computer vision we had this problem all the time, where we always let the model, like we trying to be very clever about the model where we do. Oh, let's do this pre-processing. Let's do this post-processing. It turned out the best answer, as all the Vlms have showed.
      
      525
      00:59:05.470 --> 00:59:06.670
      Vaibhav Gupta: is literally just
      
      526
      00:59:07.100 --> 00:59:15.579
      Vaibhav Gupta: give it all to the model. Let it decide, and I think the same thing is true with token, generation, or everything else too like. Don't try and be clever with token generation. Let's let the model pick the best token.
      
      527
      00:59:17.052 --> 00:59:34.890
      Vaibhav Gupta: I think that's all we have time for today in terms of actual topics and prompting techniques. I hope that this was incredibly useful for everyone else. What we'll do for the next 1520 min is I'll go to the discord, and I'll see what prompts that we have submitted, if we have any at all.
      
      528
      00:59:35.290 --> 00:59:35.810
      Vaibhav Gupta: and.
      
      529
      00:59:35.810 --> 00:59:36.930
      Dexter Horthy: There's a couple in here.
      
      530
      00:59:37.350 --> 00:59:40.069
      Vaibhav Gupta: Oh, there are! Oh, that's actually more than I expected!
      
      531
      00:59:40.993 --> 00:59:41.720
      Dexter Horthy: There's 2.
      
      532
      00:59:41.890 --> 00:59:43.740
      Vaibhav Gupta: Exact. That's more than I expected.
      
      533
      00:59:45.520 --> 00:59:47.419
      Vaibhav Gupta: Here is, I'll go. Do this.
      
      534
      00:59:47.600 --> 00:59:49.440
      Vaibhav Gupta: Let's just bring this one up.
      
      535
      00:59:51.290 --> 01:00:08.250
      Vaibhav Gupta: I use this prompt to evaluate Llms on their ability to make sense of Lm generated events. But before we go into this, does anyone have questions while I go read this prompt that people want to go, ask for, feel free to come off mute, and just ask if you, after you raise your hand and come on in.
      
      536
      01:00:11.660 --> 01:00:20.379
      Jonathan Ng: So I do have a question about that code. Gen stuff. Just because, like, when we're talking, yeah, I do agree that like letting the
      
      537
      01:00:20.510 --> 01:00:36.900
      Jonathan Ng: Codegen do its thing is much better and produces a lot better results. But, on the other hand, like, when you're working in an established code base. Usually it has its own like style and things like that.
      
      538
      01:00:37.441 --> 01:00:39.729
      Jonathan Ng: How do you resolve that problem?
      
      539
      01:00:41.710 --> 01:00:57.629
      Vaibhav Gupta: Yeah, my desk might have his own opinions. My answer for all that is always the same thing, which is just add more software on top of it. If you want stuff to be formatted in a good way, literally just run a linter on the generated code, it will be formatted exactly how you want it to be formatted.
      
      540
      01:00:57.920 --> 01:01:10.730
      Vaibhav Gupta: If you don't have a linter with an opinionated formatting, it's probably not mimicking that if you, if you feel like you don't have the linther rules. Go write a quick lm, prompt to look at your existing code, generate Linter rules off of that, and then go run the formatter
      
      541
      01:01:11.515 --> 01:01:11.990
      Vaibhav Gupta: but.
      
      542
      01:01:11.990 --> 01:01:35.149
      Dexter Horthy: Oh, because what I've seen in coding agents is a lot of like, okay, cool. Read a couple like, if you're using clock code or something. It reads a couple files, and then what it's read in the code base already kind of propagates down to the next code it generates, but it almost sounds like what would be much more efficient would be like. Take a couple of the files and have the model generate either like Hardcore Linter, because not all style can be enforced by a linter right. The linters are getting better, but not everything.
      
      543
      01:01:35.150 --> 01:01:47.560
      Dexter Horthy: but, like either, create a biome rule set or an Eslint rule set, or whatever it is, or even just create a prompt that is like, here's a bunch of examples of how we write code that. So the model doesn't have to read entire files, but you capture it succinctly.
      
      544
      01:01:47.560 --> 01:02:10.270
      Vaibhav Gupta: Yeah, and to do a little bit of extra leg work to find the models that represent it. And I think this is the same way, if you think about like just hiring a new developer, there's ways to build your Dev team where you're like. People, my dev team will just figure out some coding format and alignment. But if you really care about code quality and want it to be consistent, then you add a linter, you add a formatter, and then it becomes uniform automatically.
      
      545
      01:02:10.650 --> 01:02:25.470
      Vaibhav Gupta: So like. And the most ultimate way to do this is the end up using some language like Go, which, like forces like, if you want to export things that has to be capital like developers, don't even get a choice or use black, which is like a very opinionated python format which says, no configuration. It's just the way it is.
      
      546
      01:02:25.720 --> 01:02:28.829
      Vaibhav Gupta: and I think the same things apply for like stylistic guidelines.
      
      547
      01:02:30.740 --> 01:02:31.319
      Vaibhav Gupta: Does that.
      
      548
      01:02:31.320 --> 01:02:32.430
      Jonathan Ng: That makes sense.
      
      549
      01:02:34.244 --> 01:02:40.235
      Jonathan Ng: Yeah, I think. There's also like in cursor, for example, there are also cursor rules,
      
      550
      01:02:41.220 --> 01:02:46.980
      Jonathan Ng: which I think also help with this, although I haven't really explored a lot of it.
      
      551
      01:02:47.290 --> 01:02:48.579
      Jonathan Ng: Person would say.
      
      552
      01:02:48.580 --> 01:02:58.070
      Vaibhav Gupta: Yeah, cursor rules are a great way to go do that as well. But I think, like, if you're building an app that generates code. Then you can't use cursor rules. So then you have to build your own equivalent of cursor rules.
      
      553
      01:03:00.110 --> 01:03:12.239
      Vaibhav Gupta: That's really, if you're using cursor, then cursor rule should hopefully just fix that for you while cursor does this. Since cursor has built a system like this, they basically added a lot of software on top of their codegen
      
      554
      01:03:12.380 --> 01:03:15.420
      Vaibhav Gupta: to make their Cogen more in line with your code base.
      
      555
      01:03:16.660 --> 01:03:17.649
      Vaibhav Gupta: Oh, come on.
      
      556
      01:03:17.650 --> 01:03:20.830
      Jonathan Ng: That makes sense alright. Thank you.
      
      557
      01:03:21.310 --> 01:03:26.130
      Vaibhav Gupta: Alright, thanks, Jonathan. One last question. And then I'm gonna go into this prompt now that I've actually read it
      
      558
      01:03:29.520 --> 01:03:30.390
      Vaibhav Gupta: cool.
      
      559
      01:03:30.720 --> 01:03:34.520
      Dexter Horthy: Going once going twice, all right. Hack night of Github.
      
      560
      01:03:35.200 --> 01:03:35.890
      Vaibhav Gupta: Okay.
      
      561
      01:03:36.200 --> 01:03:44.060
      Vaibhav Gupta: So this is a prompt where it seems to be like someone wants to look at Lm, and come up with like some sort of like a plan for the most of this event.
      
      562
      01:03:44.840 --> 01:03:51.369
      Dexter Horthy: It looks like the the prompt is basically come up with a plan. And the rest of it is just input context, right?
      
      563
      01:03:51.370 --> 01:03:52.510
      Vaibhav Gupta: Yeah, exactly.
      
      564
      01:03:52.780 --> 01:03:57.099
      Vaibhav Gupta: So the 1st thing that I'll notice is like, let's just go back and write this prompt
      
      565
      01:03:59.357 --> 01:04:03.630
      Vaibhav Gupta: and actually, oh, yeah, plan, dot demo
      
      566
      01:04:06.890 --> 01:04:09.240
      Vaibhav Gupta: function, make event.
      
      567
      01:04:09.760 --> 01:04:12.959
      Vaibhav Gupta: Well, actually, I'm not gonna actually do this. I don't want this.
      
      568
      01:04:13.630 --> 01:04:14.190
      Dexter Horthy: Yeah.
      
      569
      01:04:21.290 --> 01:04:25.980
      Vaibhav Gupta: And this thing will make this a better function.
      
      570
      01:04:26.960 --> 01:04:30.620
      Vaibhav Gupta: Okay? So the 1st thing I'll notice about this is.
      
      571
      01:04:31.030 --> 01:04:35.229
      Vaibhav Gupta: oh, what the heck did. An update. Oh, that's so funny. We have a bug, we have a
      
      572
      01:04:37.150 --> 01:04:40.889
      Vaibhav Gupta: that's so funny. We have a bug where com in my.
      
      573
      01:04:40.890 --> 01:04:43.719
      Dexter Horthy: Is it coming as like Markdown, front matter or something?
      
      574
      01:04:43.720 --> 01:04:49.209
      Vaibhav Gupta: It's like dash, dash, dashes, comments. I think we strip it out that's so funny.
      
      575
      01:04:50.290 --> 01:04:51.090
      Dexter Horthy: Yes, I.
      
      576
      01:04:51.280 --> 01:04:55.620
      Vaibhav Gupta: So like the 1st thing when it comes to. So let's let's catch everyone else on what this prompt is.
      
      577
      01:04:56.210 --> 01:05:02.889
      Vaibhav Gupta: This prompt is pretty simple. It does come up with a plan to make the most of this event, and then you dump the actual event from like Luma or something else out there.
      
      578
      01:05:03.150 --> 01:05:09.409
      Vaibhav Gupta: Now. The most intuitive way is to just send that to the prompt and like, if we send the Chat, Gpt, or go, do something
      
      579
      01:05:09.580 --> 01:05:11.360
      Vaibhav Gupta: so like if I have.
      
      580
      01:05:11.360 --> 01:05:17.659
      Dexter Horthy: By the way, if whoever wrote that prompt is is here, feel free to come off mute and give a little more context around what this is, and what you use it for.
      
      581
      01:05:17.660 --> 01:05:35.410
      John Chen: Yeah, so I'm the one who posted it. This is how I you know Luma has, like a hundred events a month in San Francisco, and I don't read them all manually at first, st so I use something like this to try to surface the ones I want to go to, and this how I know about Babel. So you know a pretty crude.
      
      582
      01:05:35.410 --> 01:05:35.769
      Dexter Horthy: There you go!
      
      583
      01:05:35.770 --> 01:05:40.950
      John Chen: For me, and I just want to make it a little more comprehensive, systemic and all that.
      
      584
      01:05:41.120 --> 01:05:48.490
      John Chen: And you know I just don't have an actual process for it, but I know it. Kinda it works for me to make the sense of San Francisco texting.
      
      585
      01:05:49.020 --> 01:05:50.870
      Vaibhav Gupta: And I think I could do more with it.
      
      586
      01:05:51.600 --> 01:05:56.449
      Vaibhav Gupta: Yeah. So over here, you can see what it come up with. And this is typically what you'd expect out of this sort of thing
      
      587
      01:05:56.560 --> 01:06:08.800
      Vaibhav Gupta: that said, what I actually want is, and this is step number one, literally just stop asking the model to actually go do like, spit out the plan as a string, have the model actually spit out a preparation sub for you.
      
      588
      01:06:09.240 --> 01:06:13.369
      Vaibhav Gupta: I like what to go do. And when you actually go, do this, let's actually paste.
      
      589
      01:06:13.570 --> 01:06:15.329
      Vaibhav Gupta: I'll just copy and paste this in myself.
      
      590
      01:06:16.960 --> 01:06:21.110
      Vaibhav Gupta: I think I copied and pasted this example as well. So I'll make this test case
      
      591
      01:06:23.490 --> 01:06:25.944
      Dexter Horthy: I like the discord, only lets you copy one time.
      
      592
      01:06:26.630 --> 01:06:28.289
      Vaibhav Gupta: I know that's so funny.
      
      593
      01:06:32.330 --> 01:06:40.080
      Vaibhav Gupta: Great. So I have this test case now, and when I go run the instead of the model actually spitting this stuff up here. It's actually giving me something a little bit better
      
      594
      01:06:40.530 --> 01:06:50.320
      Vaibhav Gupta: of like what I can go talk to. And in this case I have a way, better experience like who I actually should go meet. And I can make this more targeted by simply just changing my schema
      
      595
      01:06:50.460 --> 01:06:53.000
      Vaibhav Gupta: class networking.
      
      596
      01:06:53.780 --> 01:06:54.800
      Vaibhav Gupta: Oh, God!
      
      597
      01:06:55.320 --> 01:07:00.610
      Vaibhav Gupta: Class. Networking opportunity.
      
      598
      01:07:04.880 --> 01:07:18.020
      Vaibhav Gupta: Okay. Name, season, string, value, value, high medium, low description. How valuable the.
      
      599
      01:07:18.530 --> 01:07:20.590
      Dexter Horthy: Yeah, we'll we'll push all this. Go, John.
      
      600
      01:07:20.590 --> 01:07:29.260
      Vaibhav Gupta: The person is to myself and my career polls.
      
      601
      01:07:29.810 --> 01:07:42.229
      Dexter Horthy: Yeah, the other thing, I think, would benefit a lot here is like a lot more context about me and who I am, although I guess if you're probably pasting this into Chat Gpt, then you have your memory and stuff at play to kind of like, give that grounding.
      
      602
      01:07:42.750 --> 01:07:53.100
      Vaibhav Gupta: So the name main thing that you'll notice here is I, I'm actually gonna change this. I'm gonna make this a lot better. I'm gonna say that this is I wanna meet these people value. And then it's gonna dump out the reason for why.
      
      603
      01:07:53.380 --> 01:07:59.349
      Vaibhav Gupta: And you notice that actually changed out a lot of the more general, generally specific ones like this was very
      
      604
      01:08:00.030 --> 01:08:04.559
      Vaibhav Gupta: like random, but this is a lot more pointed, oriented. I can go act on this.
      
      605
      01:08:04.700 --> 01:08:07.179
      Vaibhav Gupta: What else I can do here is, I can say, like.
      
      606
      01:08:07.390 --> 01:08:09.880
      Vaibhav Gupta: I can actually change this. I like entity
      
      607
      01:08:13.960 --> 01:08:26.500
      Vaibhav Gupta: last company, right company, name, last person, type.
      
      608
      01:08:27.029 --> 01:08:30.369
      Vaibhav Gupta: And see you want this.
      
      609
      01:08:30.960 --> 01:08:45.810
      Vaibhav Gupta: And now, when I go run this, it should actually spit out what I actually want. So now, I can actually go like specifically look these up. And I can build a small little ui around this like a react component that actually renders these in with like Linkedin searches and follow up sequences on top of that.
      
      610
      01:08:46.270 --> 01:08:58.950
      Vaibhav Gupta: So then I can just go ahead and say, Oh, here's a link to the company's URL. Here's who they are, and here's how they are. And this is just like Aiml. Speakers cool. No one specific was highlighted on there. So I don't actually have, like anyone ambiguous people are ambiguous. There.
      
      611
      01:08:59.420 --> 01:09:23.650
      Dexter Horthy: But if you put 1st name last name you could also probably force it to like it wouldn't even output that right like if you. Wanna if you want to drive the output to the point where it's like, Okay, I only want things that are actually useful. I don't want this kind of like hallucinating, sloppy like talk to aiml speakers like, Okay, that's bullshit, like I. I only want like you to pull out people with actual names. So it's like, if there was a speaker name in the description of like, this person will be speaking, then it could go tell you some things about them.
      
      612
      01:09:28.160 --> 01:09:31.730
      Vaibhav Gupta: And we can guarantee that at least the 1st name or the last name exists.
      
      613
      01:09:32.340 --> 01:09:34.890
      Vaibhav Gupta: and then all other entities will just get dropped.
      
      614
      01:09:36.420 --> 01:09:37.999
      Vaibhav Gupta: So we still get these.
      
      615
      01:09:38.370 --> 01:10:04.459
      Vaibhav Gupta: But then we they actually just get dropped from our final parsing, because, like, it doesn't meet the constraint that we need, which is 1st and last name need to actually exist. So even if they all generates it, you can drop it. But the whole point of this is, instead of actually having the model spit out the string. What I really did is I focus on what I care about what I want to see and what I want to personally derive out of this prompt, which is, I think, what John you're trying to do is like, see if things are going to help you like grow out of these events.
      
      616
      01:10:04.590 --> 01:10:09.549
      Vaibhav Gupta: So then I would just focus the specific stuff on here to say, like.
      
      617
      01:10:09.970 --> 01:10:14.919
      Vaibhav Gupta: focus on how it helps me and myself. It is to myself and my career, goals.
      
      618
      01:10:15.250 --> 01:10:23.969
      Dexter Horthy: Yeah, guide the reasoning with as much context as possible. And I bet if you took this Json object and dropped into V 0, you could make a nice ui for this, and you know 60 seconds.
      
      619
      01:10:24.620 --> 01:10:30.690
      Vaibhav Gupta: Oh, yeah, I bet this is same in line with this.
      
      620
      01:10:31.170 --> 01:10:33.670
      Vaibhav Gupta: Make a ui, for
      
      621
      01:10:41.910 --> 01:10:43.610
      Vaibhav Gupta: I'll probably go do something.
      
      622
      01:10:45.025 --> 01:10:52.400
      Vaibhav Gupta: And I'll go build some out something ui for me. And now we have a full app that we can just go use directly without having to think about it.
      
      623
      01:10:54.200 --> 01:10:56.439
      Vaibhav Gupta: with small little rendering stuff as well.
      
      624
      01:10:57.120 --> 01:10:58.909
      Vaibhav Gupta: Come on. This takes a while.
      
      625
      01:10:59.440 --> 01:11:01.520
      Vaibhav Gupta: and then you can. Do you want with your app?
      
      626
      01:11:04.200 --> 01:11:05.319
      Dexter Horthy: We got time for one more prompt
      
      627
      01:11:09.200 --> 01:11:11.120
      Dexter Horthy: saw someone else typing in.
      
      628
      01:11:12.540 --> 01:11:13.579
      sahil: Sorry. Go ahead.
      
      629
      01:11:13.850 --> 01:11:16.700
      sahil: Can I just drop the prompt in the chat, or should I.
      
      630
      01:11:16.700 --> 01:11:20.709
      Vaibhav Gupta: I'll probably be too long, but you will have to do it in the discord sadly.
      
      631
      01:11:20.710 --> 01:11:21.999
      sahil: Oh, yeah, yeah, okay. Cool.
      
      632
      01:11:22.000 --> 01:11:28.049
      Dexter Horthy: Prashant had another one as well. That was answering questions with like verbosity, and things like that.
      
      633
      01:11:28.050 --> 01:11:31.960
      Prashanth Rao: Yeah. So so actually, you kind of answered many of these in the previous example.
      
      634
      01:11:31.960 --> 01:11:32.809
      Vaibhav Gupta: Have a nice day.
      
      635
      01:11:33.510 --> 01:11:34.150
      Dexter Horthy: Okay.
      
      636
      01:11:36.336 --> 01:11:42.150
      Vaibhav Gupta: And then we'll do the last one really fast. While we're out here, and let's while while visa is loading.
      
      637
      01:11:43.540 --> 01:11:47.350
      Vaibhav Gupta: I hate this. I. This is the part I hate the most about. V. 0, it takes so long.
      
      638
      01:11:49.120 --> 01:11:50.050
      Vaibhav Gupta: Okay, well.
      
      639
      01:11:50.050 --> 01:11:52.090
      Dexter Horthy: Lot of deterministic code.
      
      640
      01:11:53.280 --> 01:11:57.890
      Vaibhav Gupta: You are tasked with a video editing plan. Okay, I'm gonna.
      
      641
      01:11:57.890 --> 01:11:58.560
      Dexter Horthy: Sick.
      
      642
      01:11:59.180 --> 01:12:05.699
      Vaibhav Gupta: Okay, I'm just gonna go do this alright. So right over here. By the way, we can see this.
      
      643
      01:12:06.730 --> 01:12:15.569
      Vaibhav Gupta: So now it has a fun, little ui for me to go. Do build this in not not to edit, just to view the final outcome.
      
      644
      01:12:16.460 --> 01:12:17.170
      Vaibhav Gupta: Oh.
      
      645
      01:12:21.990 --> 01:12:26.050
      Dexter Horthy: Oh, do you find the frowny face makes Vercel make better content.
      
      646
      01:12:26.220 --> 01:12:28.779
      Vaibhav Gupta: No, I was just annoyed that it did the wrong thing.
      
      647
      01:12:30.070 --> 01:12:30.770
      Vaibhav Gupta: Video.
      
      648
      01:12:30.770 --> 01:12:33.749
      Dexter Horthy: Well, maybe if you went and read your prompt.
      
      649
      01:12:35.320 --> 01:12:39.409
      Vaibhav Gupta: That. Well, I can't read the V 0 prompt. So it's a little bit harder.
      
      650
      01:12:40.351 --> 01:12:46.129
      Vaibhav Gupta: Insert script expert here. What is this trying to do. Do you have your? Do you have your data models and everything else on here?
      
      651
      01:12:48.160 --> 01:13:01.359
      Vaibhav Gupta: If you don't, then I I can try. But it's harder to do without like actual function types, because this prompt is a little bit more complex. But let me just give you some general guidelines that I see right off this right off my top right off the top of my head
      
      652
      01:13:01.780 --> 01:13:06.779
      Vaibhav Gupta: when I read this from the 1st thing that I see is.
      
      653
      01:13:07.220 --> 01:13:11.779
      Vaibhav Gupta: I don't actually think you need all this data like this is a lot more redundant.
      
      654
      01:13:12.000 --> 01:13:26.370
      Vaibhav Gupta: You're I'm not sure if this is all a system prompt or a user prompt. But when I go look at this, the 1st thing that I see is that this is not it's like mixing and matching both the content and the instructions all over the place.
      
      655
      01:13:26.580 --> 01:13:34.229
      Vaibhav Gupta: because, like you're listing out your, you have instructions, content instructions, content, instructions.
      
      656
      01:13:35.070 --> 01:13:38.270
      Vaibhav Gupta: instructions. It looks like more content.
      
      657
      01:13:38.580 --> 01:13:40.580
      Dexter Horthy: Oh, that's this is the output schema.
      
      658
      01:13:40.580 --> 01:13:43.810
      Vaibhav Gupta: Oh, this is the output format. Yeah, so it looks like you're.
      
      659
      01:13:43.810 --> 01:13:45.370
      Dexter Horthy: But then there's more instructions.
      
      660
      01:13:45.370 --> 01:13:49.120
      Vaibhav Gupta: Yeah, it just feels like you're we're mixing a lot of instructions, and it doesn't read
      
      661
      01:13:49.685 --> 01:13:53.270
      Vaibhav Gupta: in the way that I would write this if I were a human.
      
      662
      01:13:53.470 --> 01:14:10.579
      Vaibhav Gupta: And we're also writing a lot of things that's like you are a blah blah blah like the model doesn't care who it is, it just has to know the job it wants to do. You don't need to tell it. This is my role. If you notice in any of the prompts. I didn't. I didn't like. I wasn't like you're a senior engineer that does blah blah blah. I just like write the code from this prompt.
      
      663
      01:14:11.170 --> 01:14:13.719
      Vaibhav Gupta: That's like the 1st thing I would do. So let's just like.
      
      664
      01:14:14.090 --> 01:14:19.030
      Vaibhav Gupta: there you go. And, by the way, for people generating this, now, you can generate this kind of ui automatically from here.
      
      665
      01:14:19.380 --> 01:14:32.990
      Vaibhav Gupta: and this would be super super easy for me to go coach, and then I could put buttons on here that I'll call like Enrich, which calls another Lm function that finds all the data about that company using like a research thing that I go built. Sorry I context which really fast.
      
      666
      01:14:35.130 --> 01:14:42.379
      Vaibhav Gupta: But let me go back really fast and start a new chat thing make this prompt better.
      
      667
      01:14:42.770 --> 01:14:50.440
      Vaibhav Gupta: No. Xml and the error rendering Markdown is the thing that hopefully we'll fix in.
      
      668
      01:14:51.050 --> 01:15:09.330
      Dexter Horthy: Yeah, prashant the the ura. We were just talking about this before the episode that, like asking models to adopt a role is, I think the best prompt engineers out there have been talking for months about, if not longer, about how that doesn't really work very well or like. It doesn't have that much effect on the output.
      
      669
      01:15:09.770 --> 01:15:17.339
      sahil: The funny thing is that this comes right out of Claude from generation as well.
      
      670
      01:15:19.330 --> 01:15:20.949
      Vaibhav Gupta: I bet this is my.
      
      671
      01:15:20.950 --> 01:15:25.029
      Dexter Horthy: Because there's a lot of data in the training set doesn't mean it's correct or good data.
      
      672
      01:15:25.480 --> 01:15:29.839
      Vaibhav Gupta: Yeah, just like the most code out there is kind of shit you probably shouldn't follow most code.
      
      673
      01:15:31.045 --> 01:15:31.600
      Vaibhav Gupta: But
      
      674
      01:15:33.300 --> 01:15:40.390
      Vaibhav Gupta: a lot of code is still very good, and you should follow that. But it's all about finding the right segments. So in this case the 1st thing I do is like, get rid of this.
      
      675
      01:15:42.480 --> 01:15:50.800
      Vaibhav Gupta: create a segmentation plan for the following trip. Breaking logic for each segment, ensure it contains complete thought or idea. Estimate a reasonable time. Consider the pacing
      
      676
      01:15:51.445 --> 01:15:55.130
      Vaibhav Gupta: and it's important to kind of like, describe what these mean
      
      677
      01:15:55.540 --> 01:16:04.009
      Vaibhav Gupta: cause it probably doesn't actually know. And I I have no idea what it actually means for fast, slower medium like, I'm just it just made stuff up. You need to go and actually understand your own.
      
      678
      01:16:04.550 --> 01:16:07.780
      Vaibhav Gupta: I think, for that and like, if you.
      
      679
      01:16:07.780 --> 01:16:19.930
      Dexter Horthy: Or you could even force it in the schema. Right? You could be like, Okay, cool. I know how long this is, and I can say. I know I want exactly, you know. Do it in code, and say, I want exactly 40 cuts, because I want 30 to 40 cuts versus something else.
      
      680
      01:16:20.400 --> 01:16:22.510
      Vaibhav Gupta: I want a.
      
      681
      01:16:23.390 --> 01:16:25.750
      Dexter Horthy: Because then we're not making the model count.
      
      682
      01:16:35.280 --> 01:16:35.870
      Dexter Horthy: There you go.
      
      683
      01:16:35.870 --> 01:16:38.499
      Vaibhav Gupta: And instead of actually outputting all the stuff.
      
      684
      01:16:39.240 --> 01:16:42.119
      Vaibhav Gupta: I will actually just literally tell the model to go. Do this.
      
      685
      01:16:42.230 --> 01:16:50.589
      Vaibhav Gupta: I will literally tell it exactly what I want the pacing to be. Instead of describing all the pacings, I will specifically only admit the pacing that's actually relevant to the model.
      
      686
      01:16:50.880 --> 01:17:00.549
      Dexter Horthy: And that's the same thing, the user and the program. See a single world fast. But then you translate that into more verbose instructions, but only the Llm. Sees that part.
      
      687
      01:17:00.740 --> 01:17:07.150
      Vaibhav Gupta: And the Lm. Is not seeing everything else. So if I change this from slow to fast, it sees this one, whereas in this one it sees slow.
      
      688
      01:17:08.820 --> 01:17:12.369
      Vaibhav Gupta: right? So now it's able to actually go. Do this along the way.
      
      689
      01:17:13.204 --> 01:17:14.859
      Vaibhav Gupta: And now, when I.
      
      690
      01:17:14.860 --> 01:17:15.769
      Dexter Horthy: You can run it.
      
      691
      01:17:16.060 --> 01:17:17.540
      Vaibhav Gupta: Why not? Yeah? Why not?
      
      692
      01:17:21.090 --> 01:17:25.060
      Vaibhav Gupta: And I don't even know what transition is like. If transitions have a separate cut
      
      693
      01:17:25.670 --> 01:17:27.390
      Vaibhav Gupta: like, sure, let's do that.
      
      694
      01:17:28.520 --> 01:17:30.670
      Vaibhav Gupta: Let's let's just run this way.
      
      695
      01:17:33.390 --> 01:17:38.660
      Vaibhav Gupta: and it's able to go do this. Now. Duration is kind of is kind of misleading, and the description is kind of
      
      696
      01:17:40.470 --> 01:17:42.000
      Vaibhav Gupta: 30 seconds.
      
      697
      01:17:42.460 --> 01:17:43.770
      Vaibhav Gupta: I'm gonna change this.
      
      698
      01:17:46.690 --> 01:17:47.680
      Vaibhav Gupta: Alias.
      
      699
      01:17:53.430 --> 01:17:59.470
      sahil: I don't think we need duration, because the duration is essentially the content, so we can skip it.
      
      700
      01:17:59.470 --> 01:18:07.730
      Vaibhav Gupta: Yes, but you might benefit from actually having a duration in there, just so that a model can like plan
      
      701
      01:18:08.080 --> 01:18:09.260
      Vaibhav Gupta: for each segment.
      
      702
      01:18:09.870 --> 01:18:11.839
      Vaibhav Gupta: It's the same thing. It's like.
      
      703
      01:18:11.840 --> 01:18:13.189
      Dexter Horthy: Duration. Kind of Right.
      
      704
      01:18:13.490 --> 01:18:29.010
      Vaibhav Gupta: Cause you have. You have a thing in there where you're thinking about prompting, but you want the model to also be thinking about duration like the amount of inference it has. It's about the amount caches. Why do we have a Redis cache? Not because we can't go to the database because we don't want to go to the database all the time.
      
      705
      01:18:29.180 --> 01:18:33.159
      Vaibhav Gupta: Why are you putting duration here? The model can just like kind of think about this.
      
      706
      01:18:33.550 --> 01:18:37.769
      Vaibhav Gupta: Now we see that this content is like pretty short form.
      
      707
      01:18:37.940 --> 01:18:41.000
      Vaibhav Gupta: which is totally fine. But if you want this to be the full content.
      
      708
      01:18:41.280 --> 01:18:42.700
      Vaibhav Gupta: then we can just do this.
      
      709
      01:18:43.270 --> 01:18:47.150
      Vaibhav Gupta: We can. We can guide the model to generate more text, use.
      
      710
      01:18:47.150 --> 01:18:58.189
      Dexter Horthy: I think your input test case is really is really small. I think this is actually the right, the right text straight from the input. Thing. So like, we need like a way longer script to really test this. Anyways.
      
      711
      01:18:58.830 --> 01:19:00.909
      sahil: Can I drop in a can I drop in a script?
      
      712
      01:19:01.020 --> 01:19:01.660
      sahil: I have one.
      
      713
      01:19:01.660 --> 01:19:02.510
      Vaibhav Gupta: Yeah, dropping us.
      
      714
      01:19:02.510 --> 01:19:03.679
      Dexter Horthy: Yes, that's a script.
      
      715
      01:19:05.410 --> 01:19:06.540
      Dexter Horthy: Fuck. Yeah.
      
      716
      01:19:07.240 --> 01:19:09.100
      Dexter Horthy: On the fucking. AI that works.
      
      717
      01:19:09.100 --> 01:19:09.749
      sahil: There you go.
      
      718
      01:19:10.660 --> 01:19:12.140
      sahil: History of computing.
      
      719
      01:19:13.610 --> 01:19:19.080
      Dexter Horthy: I like this, we should do this more. We should. We should take people's real problems and solve them.
      
      720
      01:19:19.820 --> 01:19:20.699
      Vaibhav Gupta: Let's run it
      
      721
      01:19:26.020 --> 01:19:26.840
      Vaibhav Gupta: right?
      
      722
      01:19:28.080 --> 01:19:29.819
      Vaibhav Gupta: So you can actually see what it did.
      
      723
      01:19:30.040 --> 01:19:32.799
      Vaibhav Gupta: It actually spit out all the content as a line.
      
      724
      01:19:34.500 --> 01:19:37.689
      sahil: But the duration seconds is 60 for everything now.
      
      725
      01:19:37.750 --> 01:19:41.309
      Dexter Horthy: Do you still want it to be a list by Bob? Or do you want to just be a single strength.
      
      726
      01:19:42.059 --> 01:19:47.280
      Vaibhav Gupta: We can. Oh, sorry, yes, estimated
      
      727
      01:19:48.780 --> 01:19:54.030
      Vaibhav Gupta: seconds. Let's give it some description like, what? How? How do you estimate duration?
      
      728
      01:19:57.253 --> 01:20:04.980
      sahil: Let's say every 1,000 characters is a minute or 60 seconds, or.
      
      729
      01:20:05.850 --> 01:20:08.709
      Dexter Horthy: Oh, are we gonna make the model count characters.
      
      730
      01:20:09.870 --> 01:20:12.009
      Vaibhav Gupta: Every like. Let's let's try this. I want that.
      
      731
      01:20:12.010 --> 01:20:18.490
      sahil: Every every so typically every 1 20 boats per minute. So
      
      732
      01:20:19.027 --> 01:20:22.399
      sahil: there you can count words or characters. I don't know.
      
      733
      01:20:23.200 --> 01:20:26.850
      Vaibhav Gupta: Words per minute, what is average
      
      734
      01:20:28.870 --> 01:20:31.249
      Vaibhav Gupta: right? And we might actually find that like, hey.
      
      735
      01:20:31.370 --> 01:20:36.399
      Vaibhav Gupta: if we do this, it's actually when we do slower pacing. It's gonna be a little bit. It's about a hundred words per minute.
      
      736
      01:20:38.120 --> 01:20:43.840
      Vaibhav Gupta: If we do this, it's gonna be like a hundred 20, and we do fast. It's gonna be like a hundred 50.
      
      737
      01:20:44.490 --> 01:20:53.829
      Vaibhav Gupta: So you might actually like find that it's useful to actually guide the model appropriately for the different use cases, because that's what I would do. I would I would have a slightly talk faster voice in general, not just like the pacing.
      
      738
      01:20:57.480 --> 01:21:03.769
      Dexter Horthy: It would be interesting to also have this like start suggesting like, Hey, what do you want to show on the screen during this cut? Right.
      
      739
      01:21:04.360 --> 01:21:05.900
      Vaibhav Gupta: Exactly so now.
      
      740
      01:21:05.900 --> 01:21:08.140
      Dexter Horthy: Do like a image, search and pull that in.
      
      741
      01:21:08.530 --> 01:21:11.119
      Vaibhav Gupta: Background image. So let's do that.
      
      742
      01:21:12.690 --> 01:21:21.849
      Dexter Horthy: This would be a fun building, like an example of this end to end of like, how to just like generate automated video content from little scripts, an end to end content. Pipeline.
      
      743
      01:21:23.560 --> 01:21:26.769
      sahil: To make you can come, help me build my my company.
      
      744
      01:21:27.440 --> 01:21:31.762
      Dexter Horthy: I was gonna say, yeah, we have to be careful not to build a open source competitor to sail.
      
      745
      01:21:31.990 --> 01:21:34.540
      sahil: I would love for that.
      
      746
      01:21:37.995 --> 01:21:44.529
      Vaibhav Gupta: a description description, that is, that is.
      
      747
      01:21:44.760 --> 01:22:00.249
      sahil: So I have a couple of questions over here. So earlier in the example you were, you were showing how we can create indexes, and to to make sure that we are not spitting out so much text and saving tokens. I know, like, obviously, this is slightly
      
      748
      01:22:01.110 --> 01:22:06.819
      sahil: different case where we have to spit out the text. Are there any tips or tricks we could use to
      
      749
      01:22:08.050 --> 01:22:12.209
      sahil: do that index thing in here in any way, shape or form?
      
      750
      01:22:12.850 --> 01:22:21.669
      Vaibhav Gupta: Well, I don't actually know if you have to spit out the text and form like, honestly, you could just make this a lookup table based on strings like you just spit out every line, every sentence into itself.
      
      751
      01:22:22.560 --> 01:22:25.640
      Vaibhav Gupta: As like a thing, and then you could have the model spit out like a span.
      
      752
      01:22:26.700 --> 01:22:33.580
      Vaibhav Gupta: so like from dialogue, one to dialog. 7. Do this dialogue one to 3, and they'll naturally find breakpoints
      
      753
      01:22:34.040 --> 01:22:52.539
      Vaibhav Gupta: in the dialog. And now you can go. Do that. You can ask. You can build a separate pipeline that says, if you really care about like cost and latency, I would build a separate pipeline that says, Given all these dialogues, what is the most intuitive breakpoints to inject into here, and then you go get, generate the background, image and everything off of that.
      
      754
      01:22:53.260 --> 01:22:59.359
      Vaibhav Gupta: So you can solve this problem in many different ways, but it's more about identifying the indexes of where the breakpoint should be, for where transition should happen.
      
      755
      01:23:00.290 --> 01:23:10.490
      Dexter Horthy: Oh, so it becomes similar to kind of almost the diarization where maybe you just wanted to output like the first, st like the the biggest, like the smallest unique chunk that like offsets the text. There.
      
      756
      01:23:10.860 --> 01:23:13.059
      Vaibhav Gupta: Exactly cool. Exactly. Where would you go?
      
      757
      01:23:15.150 --> 01:23:15.690
      Dexter Horthy: Cool.
      
      758
      01:23:15.690 --> 01:23:27.579
      Dexter Horthy: We're 90 min, we should probably wrap it up. This was super fun. Y'all. Thank you so much by Bob for sharing your prompting wisdom for those of you who made it to the very end. Congrats. Well, there's no prize except that you got to learn more.
      
      759
      01:23:27.790 --> 01:23:35.251
      Dexter Horthy: and we will push all the code and the video, and we'll send out a blast. And come catch us next week and
      
      760
      01:23:35.680 --> 01:23:44.499
      Dexter Horthy: we should figure out what we're gonna do. Next week we have a we have a, we have a long backlog of things, but we're gonna figure it out, and we'll we'll we'll update y'all with what's coming next. So thanks, everybody.
      
      761
      01:23:45.220 --> 01:23:45.730
      Vaibhav Gupta: Thanks for joining.
      
      762
      01:23:46.200 --> 01:23:47.110
      Aaron Lehman | LifeLensAR: Thanks. Y'all.
      
      763
      01:23:47.580 --> 01:23:48.289
      Dexter Horthy: See ya.
      
      
    "#
    video_title #"Cracking the Prompting Interview"#
  }
}