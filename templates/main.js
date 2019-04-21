{% load static %}
<script type="text/javascript">

var socket = new WebSocket("ws://" + window.location.host);

var my_profile = '';
var choose = $("#id_choose");
var roomDict = {}
var i;

function appendMessage(html) {
  $("#messages").append(html);
  var objDiv = document.getElementById("chat_area");
  objDiv.scrollTop = objDiv.scrollHeight;
}

function sendRoomAction(action, room, target) {
  var msg = {
    room: room,
    type: action,
    target: target
  }
  socket.send(JSON.stringify(msg));
}

function room(id) {
  this.id = id
  this.socket = socket;
  this.messages = ""
  this.typed = ""
  var self = this;
  $.get("chat/" + this.id + "/", function(data) {
    self.messages += data;
  })

  this.handleMessage = function(data) {
    date = new Date().toISOString()
    type = data.type;
    $("#no-messages-"+this.id).css("display", "none");

    switch(type) {
      case "message": {
          var html = `<li class="message"><span><img src=`
          + `"{% static 'images/default.jpg' %}"`
          + `class="pointer ${data.user}"></span>`
          + `<span class="message-span"><div><h5>`
          + `${data.content}</h5></div>`
          + `</span><span class="timestamp">`
          + `${date.slice(0,10)} ${date.slice(11,19)}</span>`
          
          this.messages += html

          $("#latest"+this.id).html(data.user + ': ' + data.content)

          if(i==this.id) {         
            appendMessage(html);
          } 
          else {
            $("#"+this.id).effect("highlight", {color: '#add8e6'}, 2000);
          }
          $("#"+this.id).parent().prepend($("#"+this.id))
          $("#id_timestamp_"+this.id).html(date.slice(11,16))
          break;
        }

      case "notify": {
          var html = `<li class="room-notify"><b>${data.content}`
                    + `</b></li>`
          $("#latest"+this.id).html(data.content);
          $("#"+this.id).parent().prepend($("#"+this.id))
          $("#id_timestamp_"+this.id).html(date.slice(11,16))
          if(i==this.id) {         
            appendMessage(html);
          }
        }
    }
    }
    this.sendMessage = function() {
      var txt = $("#message_text").val()
      if(txt != '') {
        var msg = {
          type: "message",
          room: this.id,
          msg: txt
        }
        socket.send(JSON.stringify(msg));
        $("#latest"+this.id).html("{{ request.user }}" + ': ' + txt);
        $("#message_text").val('');
      }
    } 
}



$(document).ready(function() {

  {% for room in chats %}

  roomDict[{{ room.pk }}] = new room({{ room.pk }});

   $("#{{ room.pk }}").click(function(e) {
        e.preventDefault();
        if (i != null) {
          roomDict[i].typed = $("#message_text").val()
        }
        i = {{ room.pk }};
        $("#message_text").val(roomDict[{{ room.pk }}].typed)
        
        sendRoomAction("open", {{ room.pk }}, "");

        if($(window).width() <= 640) {
          $(".menu").css("display", "none")
          $(".chat-area").css("display", "inline")
          $(".back-btn").css("display", "inline")
        }
        
        $("#chat_area").html('<ul class="list-unstyled" id="messages">'
            + roomDict[{{ room.pk }}].messages
            + '   </ul>');
        
        var objDiv = document.getElementById("chat_area");
        objDiv.scrollTop = objDiv.scrollHeight;

        $("#send_button").off("click").click(function(e) {
          roomDict[{{ room.pk }}].sendMessage();
        });

        $("#message_text").focus();
        $(".write-section").css("display", "block")
        $(".open-room-bar").css("display", "block")
        $(".open-room-bar").html("<div class='bar-content'" + 
          " id='room-name-{{ room.pk }}'><img src={% static "images/default.jpg" %}><b>{{ room.name }}" + 
          "</b><div id='id_online_{{ room.pk }}'>{{ room.online }}</div></div>")

      $("#room-name-{{ room.pk }}").click(function(e) {
        e.preventDefault();
        $.get(window.location.href + "chatroom/{{ room.pk }}/", function(data) {
        $(".modal-content").html(data);
        $("#myModal").css("display", "block");
      })
      
    })

    });
    
    {% endfor %}

  var username = "{{ request.user.username }}"
  var messages = ""
  
  $(".msg").dotdotdot({});

  socket.onmessage = function(e) {
    data = JSON.parse(e.data);
    room = data.room
    
    if("connect" in data) {
     $.get("info/"+room+"/", function(data){
      $("#id_online_"+room).html(data.online)
      })
     return;
    };
    if("disconnect" in data) {
      $.get("info/"+room+"/", function(data){
        $("#id_online_"+room).html(data.online)
        })
      return;
    }
    else {
      roomDict[room].handleMessage(data);
      }
    }





    //send message with enter key

    $(document).keypress(function(e) {
      if ((e.which == 13 && !e.shiftKey) && 
        $(".modal").css("display")=="none"){
          e.preventDefault();
          $("#send_button").click();
          }
    });
  
	var modal = document.getElementById('myModal');
	

	// Get the button that opens the modal
	var btn = document.getElementById("profile");

	// Get the <span> element that closes the modal
	var span = document.getElementsByClassName("close")[0];

	// When the user clicks on the button, open the modal
	btn.onclick = function() {
		$.get(window.location.href + "profile/{{ request.user.username }}/", function(data) {
      		$(".modal-content").html(data);
          modal.style.display = "block";
   		})
	    
	}

	// When the user clicks on <span> (x), close the modal
	span.onclick = function() {
	    modal.style.display = "none";
	}

	// When the user clicks anywhere outside of the modal, close it

	window.onclick = function(event) {
	    if (event.target == modal) {
	        modal.style.display = "none";
	    }
	}


// close modal on esc

$(document).keydown(function(e) {
  if(e.keyCode == 27) {
  $(".modal").css("display", "none")
  }
})

// open room join menu

$("#button-join-room").click(function() {
  $.get("{% url 'room-join-menu' %}", function(data) {
    $(".modal-content").html(data);
    modal.style.display = "block";
  })
})

// open room create menu

$("#button-create-room").click(function() {
  $.get("{% url 'room-create-menu' %}", function(data) {
    $(".modal-content").html(data);
    modal.style.display="block";
  })
})

})

</script>