var moving_piece = null;
var move_from = "";
var move_to = "";
var piece_captured = "";
var current_player = "";


// player grabs piece they wish to move
function grab(e){
    e.classList.add("active");

    if (move_from && move_from != e.id){
        e_move_from = document.getElementById(move_from);
        e_move_from.classList.remove("active");
    }

    move_from = e.id;
    moving_piece = e.innerHTML.trim();

    console.log(moving_piece);

    for (var i = 0 ; i < 8; i++){
        for (var j = 0; j < 8; j++){
            row_col = i.toString().concat(j.toString());
            e_tile = document.getElementById(row_col);
            tile_onclick = e_tile.getAttribute("onclick");
            if (tile_onclick != "grab(this)"){
                e_tile.setAttribute("onclick", "drop(this)");
                e_tile.classList.add("pointer")
            }
        }
    }
}

// player drops piece on tile they wish to move to
function drop(e){
    e_move_from = document.getElementById(move_from);
    move_to = e.id
    piece_captured = e.innerHTML;
    
    if (move_to != move_from){

        e.innerHTML = moving_piece;
        e_move_from.innerHTML = "";

        for (var i = 0 ; i < 8; i++){
            for (var j = 0; j < 8; j++){
                row_col = i.toString().concat(j.toString());
                e_tile = document.getElementById(row_col);
                e_tile.setAttribute("onclick", "");
                e_tile.classList.remove("active", "pointer")
            }
        }
        document.getElementById(move_to).classList.add("active");
    
        console.log("recorded move: ", move_from.concat(move_to))
    }

    document.getElementById("submit_btn").style.display = "block";
    document.getElementById("submit_btn").style.width = "48%";
    document.getElementById("undo_btn").style.display = "block";
    document.getElementById("undo_btn").style.width = "48%";
}

// player submits move
async function submit(){
    console.log("submit");
    
    var e_game_id = document.getElementById("game_id");
    var game_id = e_game_id.innerHTML;
    
    var data = {
        game_id: game_id,
        move_from: move_from,
        move_to: move_to 
    }
    
    console.log(`data: ${JSON.stringify(data)}`);
    
    var settings = {
        method: "POST",
        header: {"content_type":"application/json"},
        body: JSON.stringify(data)
    }
   
    // submit the move as a POST request
    var response = await fetch('/api/games/move', settings);
    console.log(`status ${response.status}`);

    document.getElementById("submit_btn").style.display = "none";
    document.getElementById("undo_btn").style.display = "none";

    // redirect: reload current page
    location.href = `/games/${game_id}/play`;
}

// undo a move by reloading the page
function undo_move(){
    var e_game_id = document.getElementById("game_id");
    var game_id = e_game_id.innerHTML;

    location.href = `/games/${game_id}/play`;
}
