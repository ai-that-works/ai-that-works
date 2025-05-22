
enum EntityType {
	Individual
	Corporation
	Charity
	Other 
	Unknown
}


class NotAGiftEmail {
	type "not_a_gift_email"
	reasoning string
}

class GiftEmailAnalysis {
	type "gift_received" | "gift_given"
	sender string
	sender_relationship string @description("The relationship between the sender and the company")
	sender_entity_type EntityType
	recipient string
	recipient_relationship string @description("The relationship between the recipient and the company")
	recipient_entity_type EntityType
	risk_level "low" | "medium" | "high"
	reasoning string
	open_questions string[] @description("A list of questions that are relevant to the email")
	follow_up_actions string[] @description("A description of the next steps to take to answer any open questions")
}

// Create a function to extract the resume from a string.
function EvaluateGiftPolicy(email: string, company_name: string) -> NotAGiftEmail | GiftEmailAnalysis {
  // Specify a client as provider/model-name
  client "openai/gpt-4o" // Set OPENAI_API_KEY to use this client.
  prompt #"

	You are a compliance expert working at {{ company_name }}.


    Your goal is to determine whether the email
    evidence violates the policy.

	In this case, the policy is:


	Members must not accept gifts or favors from any person or entity that is a subject of the Company's business, including suppliers, customers, competitors, or other third parties.
    {{ ctx.output_format }}

    {{ _.role("user") }}

    <email>
    {{ email }}
    </email>
  "#
}


test evaluate_gift_policy_1 {
  functions [EvaluateGiftPolicy]


  args {
    company_name "Enron"

    email #"
      Message-ID: <7228326.1075840095747.JavaMail.evans@thyme>
Date: Wed, 13 Dec 2000 10:04:00 -0800 (PST)
From: rosalee.fleming@enron.com
To: james.bannantine@enron.com, cliff.baxter@enron.com, 
	sanjay.bhatnagar@enron.com, jeremy.blachman@enron.com, 
	philippe.bibi@enron.com, raymond.bowen@enron.com, 
	michael.brown@enron.com, harold.buchanan@enron.com, 
	rick.buy@enron.com, richard.causey@enron.com, 
	diomedes.christodoulou@enron.com, wade.cline@enron.com, 
	david.cox@enron.com, david.delainey@enron.com, 
	james.derrick@enron.com, steve.elliott@enron.com, 
	jim.fallon@enron.com, andrew.fastow@enron.com, 
	mark.frevert@enron.com, ben.glisan@enron.com, kevin.hannon@enron.com, 
	david.haug@enron.com, rod.hayslett@enron.com, 
	stanley.horton@enron.com, james.hughes@enron.com, 
	larry.izzo@enron.com, steven.kean@enron.com, 
	louise.kitchen@enron.com, mark.koenig@enron.com, 
	kenneth.lay@enron.com, john.lavorato@enron.com, dan.leff@enron.com, 
	danny.mccarty@enron.com, mike.mcconnell@enron.com, 
	rebecca.mcdonald@enron.com, jeffrey.mcmahon@enron.com, 
	mark.metts@enron.com, mark.muller@enron.com, cindy.olson@enron.com, 
	lou.pai@enron.com, ken.rice@enron.com, matthew.scrimshaw@enron.com, 
	jeffrey.shankman@enron.com, jeffrey.sherrick@enron.com, 
	john.sherriff@enron.com, jeff.skilling@enron.com, 
	marty.sunde@enron.com, greg.whalley@enron.com, 
	thomas.white@enron.com, g.garcia@enron.com, marcia.manarin@enron.com, 
	susan.skarness@enron.com, stacy.guidroz@enron.com, 
	beena.pradhan@enron.com, karen.heathman@enron.com, 
	sharron.westbrook@enron.com, kay.chapman@enron.com, 
	molly.bobrow@enron.com, rosane.fabozzi@enron.com, 
	stephanie.harris@enron.com, bridget.maronge@enron.com, 
	nicki.daw@enron.com, inez.dauterive@enron.com, carol.brown@enron.com, 
	elaine.rodriguez@enron.com, cindy.stark@enron.com, 
	mary.garza@enron.com, maureen.mcvicker@enron.com, 
	joannie.williamson@enron.com, vanessa.groscrand@enron.com, 
	suzanne.danz@enron.com, tori.wells@enron.com, 
	cathy.phillips@enron.com, loretta.brelsford@enron.com, 
	sue.ford@enron.com, dolores.fisher@enron.com, 
	kathy.mcmahon@enron.com, karen.owens@enron.com, 
	dorothy.dalton@enron.com, mercedes.estrada@enron.com, 
	christina.grow@enron.com, lauren.urquhart@enron.com, 
	sherri.sera@enron.com, katherine.brown@enron.com, 
	liz.taylor@enron.com, judy.smith@enron.com, peggy.mccurley@enron.com, 
	marsha.schiller@enron.com, fiona.stewart@enron.com, 
	jana.paxton@enron.com, connie.blackwood@enron.com, 
	tammie.schoppe@enron.com, kimberly.hillis@enron.com, 
	jennifer.burns@enron.com, sharon.dick@enron.com, 
	beverly.aden@enron.com, kathy.dodgen@enron.com, 
	kerry.ferrari@enron.com, carol.moffett@enron.com, 
	jennifer.adams@enron.com, leah.rijo@enron.com, 
	lucy.marshall@enron.com, kathy.campos@enron.com, 
	julie.armstrong@enron.com, kathryn.greer@enron.com, 
	mrudula.gadade@enron.com, brenda.castillo@enron.com
Subject: Thank you for the Charitygift
Mime-Version: 1.0
Content-Type: text/plain; charset=us-ascii
Content-Transfer-Encoding: 7bit
X-From: Rosalee Fleming
X-To: James M Bannantine, Cliff Baxter, Sanjay Bhatnagar, Jeremy Blachman, Philippe A Bibi, Raymond Bowen, Michael R Brown, Harold G Buchanan, Rick Buy, Richard Causey, Diomedes Christodoulou, Wade Cline, David Cox, David W Delainey, James Derrick, Steve Elliott, Jim Fallon, Andrew S Fastow, Mark Frevert, Ben F Glisan, Kevin Hannon, David Haug, Rod Hayslett, Stanley Horton, James A Hughes, Larry L Izzo, Steven J Kean, Louise Kitchen, Mark Koenig, Kenneth Lay, John J Lavorato, Dan Leff, Danny McCarty, Mike McConnell, Rebecca McDonald, Jeffrey McMahon, Mark Metts, Mark S Muller, Cindy Olson, Lou L Pai, Ken Rice, Matthew Scrimshaw, Jeffrey A Shankman, Jeffrey Sherrick, John Sherriff, Jeff Skilling, Marty Sunde, Greg Whalley, Thomas E White, G G Garcia, Marcia Manarin, Susan Skarness, Stacy Guidroz, Beena Pradhan, Karen K Heathman, Sharron Westbrook, Kay Chapman, Molly Bobrow, Rosane Fabozzi, Stephanie Harris, Bridget Maronge, Nicki Daw, Inez Dauterive, Carol Ann Brown, Elaine Rodriguez, Cindy Stark, Mary E Garza, Maureen McVicker, Joannie Williamson, Vanessa Groscrand, Suzanne Danz, Tori L Wells, Cathy Phillips, Loretta Brelsford, Sue Ford, Dolores Fisher, Kathy McMahon, Karen Owens, Dorothy Dalton, Mercedes Estrada, Christina Grow, Lauren Urquhart, Sherri Sera, Katherine Brown, Liz M Taylor, Judy G Smith, Peggy McCurley, Marsha Schiller, Fiona Stewart, Jana L Paxton, Connie Blackwood, Tammie Schoppe, Kimberly Hillis, Jennifer Burns, Sharon Dick, Beverly Aden, Kathy Dodgen, Kerry Ferrari, Carol Moffett, Jennifer Adams, Leah Rijo, Lucy Marshall, Kathy Campos, Julie Armstrong, Kathryn Greer, Mrudula Gadade, Brenda Castillo
X-cc: 
X-bcc: 
X-Folder: \Jeffrey_Skilling_Dec2000\Notes Folders\Notes inbox
X-Origin: SKILLING-J
X-FileName: jskillin.nsf

---------------------- Forwarded by Rosalee Fleming/Corp/Enron on 12/13/2000 
05:59 PM ---------------------------

Kathy Mayfield
12/13/2000 05:02 PM


To: Rosalee Fleming/Corp/Enron@ENRON
cc:  
Subject: Thank you for the Charitygift


---------------------- Forwarded by Kathy Mayfield/Corp/Enron on 12/13/2000 
04:38 PM ---------------------------


bill_morgan@kindermorgan.com on 12/13/2000 04:34:58 PM
To: kathy.mayfield@enron.com
cc:  

Subject: Thank you for the Charitygift


Thank you for the Charity Gift Card.  I decided to donate the gift to the 
Depelchin Children's Center.


 "#
  }
}