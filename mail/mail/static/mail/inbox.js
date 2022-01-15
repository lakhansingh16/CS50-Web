document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  //listen for sending mail
  document.querySelector("#compose-form").addEventListener("submit",send_mail);
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Print emails in console
    console.log(emails);
    //display emails to users
    emails.forEach(function(item){
      const element = document.createElement("div");

      generate_mailbox(item, element, mailbox);
      document.querySelector("#emails-view").appendChild(element);
      element.addEventListener('click',() => read_email(item["id"]));
    });
  });
}

//function to send a composed email using the API
function send_mail(){
  event.preventDefault();
  console.log("working");
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector("#compose-subject").value;
  const body = document.querySelector("#compose-body").value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    }),
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox("sent", result);
  });
  
}

//function to read individuals emails on getting clicked
function read_email(email_id){
  //display the required section of page
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  document.querySelector("#email-view").innerHTML = "";

  //mark email read
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })

  //load the clicked email onto page
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(result => {
    generate_mail(result);
  })
  .catch(error => console.log(error));
  console.log(email_id);
}


//function to build individual email 
function generate_mail(email){
  const sender = document.createElement("div");
  const receiver = document.createElement("div");
  const subject = document.createElement("div");
  const timestamp = document.createElement("div");
  const reply_button = document.createElement("button");
  const archive_button = document.createElement("button");
  const body = document.createElement("div");
  archive_button.classList="btn btn-outline-primary m-2"

  archive_button.addEventListener("click", () => {
    archive_email(email);
    load_mailbox("inbox");
  });

  archive_button.innerHTML="";
  if (email["archived"]) {
    archive_button.innerHTML += "Unarchive";
  } else {
    archive_button.innerHTML += "Archive";
  }
  reply_button.classList = "btn btn-outline-primary m-2";
  reply_button.addEventListener("click", () => reply_mail(email));
  reply_button.innerHTML = "Reply";

  sender.innerHTML = `<strong>From: </strong> ${email["sender"]}`;
  receiver.innerHTML = `<strong>To: </strong> ${email["recipients"].join(", ")}`;
  subject.innerHTML = `<strong>Subject: </strong> ${email["subject"]}`;
  timestamp.innerHTML = `<strong>Timestamp: </strong> ${email["timestamp"]}`;
  body.innerHTML = email["body"];
  body.className="email-body";

  document.querySelector("#email-view").appendChild(sender);
  document.querySelector("#email-view").appendChild(receiver);
  document.querySelector("#email-view").appendChild(subject);
  document.querySelector("#email-view").appendChild(timestamp);
  document.querySelector("#email-view").appendChild(archive_button);
  document.querySelector("#email-view").appendChild(reply_button);
  document.querySelector("#email-view").appendChild(body);


}

//function to generate emails according to the mailbox that the user visits
function generate_mailbox(email, parent_element, type) {
  //Exempt emails that are archived from inbox
  if (type === "inbox" && email["archived"]) {
    return;
  }
  //only archived emails go in archive mailbox
  else if (type === "archive" && !email["archived"]) {
    return;
  }

  const content = document.createElement("div");

  const receivers = document.createElement("strong");
  if (type === "sent") {
    receivers.innerHTML = email["recipients"].join(", ") + " ";
  }
  else {
    receivers.innerHTML = email["sender"] + " ";
  }
  content.appendChild(receivers);

  content.innerHTML += email["subject"];

  // Set and style the date.
  const date = document.createElement("div");
  date.innerHTML = email["timestamp"];
  date.style.display = "inline-block";
  date.style.float = "right";

  if (email["read"]) {
    parent_element.style.backgroundColor = "grey";
    date.style.color = "black";
  } else {
    parent_element.style.backgroundColor = "white";
    parent_element.style.color = "black";
    date.style.color = "black";
  }
  content.appendChild(date);

  content.style.padding = "10px";
  parent_element.appendChild(content);


  // Style the parent element.
  parent_element.className = 'email-listing';
}


//function to archive an email
function archive_email(data) {
  fetch(`/emails/${data["id"]}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: !data["archived"]
    })
  });
}



function reply_mail(email) {
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = email["sender"];//sender will now be receiver
  const matching = email["subject"].slice(0,3) === "Re:";
  if (matching){
    document.querySelector("#compose-subject").value = (email["subject"]);
  }else{
    document.querySelector("#compose-subject").value = ("Re: " + email["subject"]);
  }
  document.querySelector("#compose-body").value = `On ${email["timestamp"]} ${email["sender"]} wrote:\n${email["body"]}\n-------------------------------------\n`;
}