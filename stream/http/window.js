
// Chat Message Handling
function chat_read(chat_data)
{
    if(chat_data.length ==0)
    {
      return
    }

    chat_list = document.getElementById("chat-list");
    chat_list.textContent = '';

    chat_data.forEach((c) => {
        li = document.createElement("li");

        var name = document.createElement("span");
        name.innerHTML = c['from'];
        name.style.color = c['color'];
        name.classList.add("name");
        li.appendChild(name)

        var text = document.createElement("span");
        text.innerHTML = ": " + c['text'];
        text.classList.add("text");
        li.appendChild(text)

        chat_list.appendChild(li)
    });

}

// Subs Message Handling
sub_last_timestamp=""
function subs_read(subs_data)
{
    if(subs_data.length ==0)
    {
      return
    }

    most_recent = subs_data[subs_data.length-1]

    if ( most_recent['timestamp'] == sub_last_timestamp ) return
    sub_last_timestamp = most_recent['timestamp']

    message_box = document.getElementById("message-box");
    message_box.textContent = most_recent['text'];


    message_box.classList.add('fade-in');
    message_box.classList.remove('fade-out');
    setTimeout(subs_fade_out,10000)
}



// Poll Handling
function poll_read(poll_data)
{
    if(poll_data.length ==0)
    {
      return
    }

    if (!poll_data.valid)
    {
	    return
    }

    poll_list = document.getElementById("poll-list");
    poll_list.textContent = '';

    poll_title = document.getElementById("poll-title");
    poll_title.textContent = poll_data.title;

    for (const [key, value] of Object.entries(poll_data.data)) {

        li = document.createElement("li");

        var text = document.createElement("span");
        text.innerHTML = key+": " + value;
        li.appendChild(text)

        poll_list.appendChild(li)

    };
    poll_box = document.getElementById("poll-box");
    poll_box.classList.add('fade-in');
    poll_box.classList.remove('fade-out');
}


function subs_fade_out()
{
    message_box = document.getElementById("message-box");
    message_box.classList.add('fade-out');
    message_box.classList.remove('fade-in');
}

// Chat Data Loop
function chat_fetch()
{
  fetch('chat.json')
    .then((response) => response.json())
    .then((data) => chat_read(data));

  setTimeout(chat_fetch,1000)
}

// Subs Data Loop
function subs_fetch()
{
  fetch('subs.json')
    .then((response) => response.json())
    .then((data) => subs_read(data));

  setTimeout(subs_fetch,1000)
}

// Poll Data Loop
function poll_fetch()
{
  fetch('poll.json')
    .then((response) => response.json())
    .then((data) => poll_read(data));

  setTimeout(poll_fetch,1000)
}



// Final Init
setTimeout(chat_fetch,1000)
setTimeout(subs_fetch,1000)
setTimeout(poll_fetch,1000)
document.getElementById("message-box").classList.add('fade-out');
document.getElementById("poll-box").classList.add('fade-out');
