$(window).load(function(){
    /*
NOTE: The Trello client library has been included as a Managed Resource.  To include the client library in your own code, you would include jQuery and then

<script src="https://api.trello.com/1/client.js?key=your_application_key">...

See https://trello.com/docs for a list of available API URLs

The API development board is at https://trello.com/api

The &dummy=.js part of the managed resource URL is required per http://doc.jsfiddle.net/basic/introduction.html#add-resources
*/

  var onAuthorize = function() {
    updateLoggedIn();
    $("#output").empty();

    //Store token
    $("#token").val(Trello.token());

    Trello.members.get("me", function(member){
      $("#fullName").text(member.fullName);

      var $boards = $("<select>")
        .attr("id", "board_id")
        .attr("name", "board_id")
        .attr("class", "form-control")
        .text("Loading boards...")
        .appendTo("#output");

      Trello.get("members/me/boards", function(boards) {
        $boards.empty();
        $.each(boards, function(ix, board) {
          $("<option>")
          .attr({value: board.id})
          .text(board.name).appendTo($boards);
        })
      });
    });

  };

  var updateLoggedIn = function() {
    var isLoggedIn = Trello.authorized();
    $("#loggedout").toggle(!isLoggedIn);
    $("#loggedin").toggle(isLoggedIn);
  };

  var logout = function() {
    Trello.deauthorize();
    updateLoggedIn();
  };

  Trello.authorize({
    interactive:false,
    name: "Trexcel",
    success: onAuthorize
  });

  $("#connectLink")
  .click(function(){
    Trello.authorize({
      type: "popup",
      name: "Trexcel",
      expiration: "1hour",
      success: onAuthorize
    })
  });

  $("#disconnect").click(logout);


});
