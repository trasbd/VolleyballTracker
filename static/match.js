let currentMatchId = null;
let currentGameNumber = 0;
let lastGameId = null;
let statsMap = {};

document.addEventListener("DOMContentLoaded", async () => {
    // Fetch current match/game info
    const currentRes = await fetch("/api/current");
    const current = await currentRes.json();
    currentMatchId = current.currentMatch;
    const gameId = current.currentGame;

    if (gameId) {
        // Look up full game info to get the game_number
        const gameRes = await fetch(`/api/games/${gameId}`);
        const game = await gameRes.json();
        currentGameNumber = game.game_number;
        lastGameId = game.id;

        // Display current game number
        document.getElementById("currentGameNumber").textContent = currentGameNumber;

        // Fetch and prefill assigned players
        const assignedRes = await fetch(`/api/games/${gameId}/players`);
        const assignedIds = await assignedRes.json();

        // Wait for stat table to render
        const waitForGrid = () => new Promise(res => {
            const check = () => {
                const selects = document.querySelectorAll("#playerStatsGrid select");
                if (selects.length >= 6) res(selects);
                else setTimeout(check, 50);
            };
            check();
        });

        const selects = await waitForGrid();
        for (let i = 0; i < selects.length && i < assignedIds.length; i++) {
            selects[i].value = assignedIds[i];
            selects[i].dispatchEvent(new Event("change"));
        }
    }




    if (currentMatchId) {
        // Fetch and display scores for all games in the match
        const gameResults = [
            document.getElementById("game1Result"),
            document.getElementById("game2Result"),
            document.getElementById("game3Result")
        ];

        // Clear all scores first
        gameResults.forEach(el => el.textContent = "—");

        const matchGamesRes = await fetch(`/api/match/${currentMatchId}/games`);
        const allGames = await matchGamesRes.json();

        allGames.forEach(game => {
            if (game.game_number >= 1 && game.game_number <= 3) {
                const str = (game.score !== null && game.score_opponent !== null)
                    ? `${game.score}-${game.score_opponent}`
                    : "—";
                gameResults[game.game_number - 1].textContent = str;
            }
        });

        // Enable New Game button
        document.getElementById("newGameBtn").disabled = false;

        // Optionally: Fetch match metadata and populate UI
        const matchMeta = await fetch("/api/matches").then(res => res.json());
        const match = matchMeta.find(m => m.id === currentMatchId);
        if (match) {
            const matchDate = new Date(match.date_time).toLocaleString();
            document.getElementById("matchDate").textContent = matchDate;
            document.getElementById("matchCourt").textContent = match.court_number || "—";
            document.getElementById("matchOpponent").textContent = match.opponent || "—";
        }
    }

    // (Rest of your stat table population code continues below...)
});


document.addEventListener("DOMContentLoaded", async () => {
    const statGroups = {
        Serve: ["Ace", "ServiceError"],
        Attack: ["Kill", "AttackError"],
        Block: ["Block"],
        Dig: ["Dig"],
        Reception: ["Reception", "ReceptionError"],
        Assist: ["Assist"],
        Touch: ["Touch", "Saves"],

    };

    const statToString = {
        ServiceError: "Error",
        AttackError: "Error",
        ReceptionError: "Error"
    }

    const grid = document.getElementById("playerStatsGrid");

    const players = await fetch("/api/players").then(res => res.json());
    statsMap = {};
    const existingStats = await fetch("/api/stats").then(res => res.json());
    existingStats.forEach(s => statsMap[s.player_id] = s);

    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";
    table.style.marginBottom = "2rem";

    // Top header: category names with colspan
    const header1 = document.createElement("tr");
    const thName = document.createElement("th");
    thName.rowSpan = 2;
    thName.textContent = "Player";
    header1.appendChild(thName);

    for (const group in statGroups) {
        const th = document.createElement("th");
        th.colSpan = statGroups[group].length;
        th.textContent = group;
        header1.appendChild(th);
    }
    table.appendChild(header1);

    // Subheader: actual stat names

    const header2 = document.createElement("tr");
    /*
    for (const group in statGroups) {
      statGroups[group].forEach(statName => {
        const th = document.createElement("th");
        th.textContent = statName;
        header2.appendChild(th);
      });
    }
      */
    table.appendChild(header2);


    const NUM_ACTIVE = 6;

    // Fill 6 player slots
    for (let i = 0; i < NUM_ACTIVE; i++) {
        const row = document.createElement("tr");
        const row2 = document.createElement("tr");

        // Create player dropdown
        const tdName = document.createElement("td");
        tdName.rowSpan = 2;

        const select = document.createElement("select");

        // Add "None" option
        const noneOption = document.createElement("option");
        noneOption.value = "";
        noneOption.textContent = "— None —";
        select.appendChild(noneOption);

        // Add players to dropdown
        players.forEach(p => {
            const option = document.createElement("option");
            option.value = p.id;
            option.textContent = `#${p.jersey} ${p.name}`;
            select.appendChild(option);
        });


        tdName.appendChild(select);
        row.appendChild(tdName);

        // Track buttons + total cells so we can update them later
        const buttons = {};
        const totalCells = {};

        for (const group in statGroups) {
            let groupTotal = 0;

            statGroups[group].forEach(statName => {
                const td = document.createElement("td");
                const btn = document.createElement("button");

                btn.style.width = "100%";

                td.appendChild(btn);
                row.appendChild(td);

                buttons[statName] = btn;
            });

            const totalTd = document.createElement("td");
            /*
            totalTd.colSpan = statGroups[group].length;
            totalTd.style.textAlign = "center";
            totalTd.style.fontWeight = "bold";
            row2.appendChild(totalTd);
            */
            totalCells[group] = totalTd;
        }

        // Function to update stat buttons when player changes
        async function updatePlayerStats(playerId) {
            if (!playerId) {
                // If "None" selected, clear all buttons and disable them
                for (const statName in buttons) {
                    buttons[statName].textContent = "-";
                    buttons[statName].disabled = true;
                    buttons[statName].classList.add("table-button");

                }
                for (const group in totalCells) {
                    totalCells[group].textContent = "";
                }
                return;
            }

            const stat = statsMap[playerId] || {};
            for (const group in statGroups) {
                let groupTotal = 0;
                statGroups[group].forEach(statName => {
                    const count = stat[statName] || 0;
                    buttons[statName].textContent = `${statToString[statName] || statName}: ${count}`;
                    buttons[statName].disabled = false;

                    if (statName.includes("Error")) {
                        buttons[statName].classList.add("delete-btn");
                    }
                    else {
                        buttons[statName].classList.add("table-button");
                    }
                    groupTotal += count;
                });
                totalCells[group].textContent = `Total: ${groupTotal}`;
            }
        }


        // Hook up button actions
        for (const group in statGroups) {
            statGroups[group].forEach(statName => {
                buttons[statName].onclick = async () => {
                    const playerId = select.value;
                    const res = await fetch(`/api/stats/${currentMatchId}/${currentGameNumber}/${playerId}`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ [statName]: 1 })
                    });

                    if (res.ok) {
                        const updated = await res.json();
                        statsMap[playerId] = updated; // update local stat map
                        updatePlayerStats(playerId);  // refresh button counts
                    }
                };

            });
        }

        // On dropdown change, refresh stats
        select.addEventListener("change", async () => {
            const playerId = select.value;
            await updatePlayerStats(playerId);

            // Save the new assignment if we're in an active game
            if (lastGameId && playerId) {
                await fetch(`/api/games/${lastGameId}/players`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ players: [playerId] })
                });
            }
        });


        // Don't auto-select; default to "None"
        select.selectedIndex = 0;
        updatePlayerStats(null);

        table.appendChild(row);
        table.appendChild(row2);
    }




    grid.appendChild(table);
});


const newMatchBtn = document.getElementById("newMatchBtn");
const newGameBtn = document.getElementById("newGameBtn");
const matchModal = document.getElementById("newMatchModal");
const matchForm = document.getElementById("newMatchForm");

newMatchBtn.onclick = async () => {
    matchModal.style.display = "flex";

    const res = await fetch(`/api/nextmatch`, { method: "GET" });

    if (res.ok) {
        const match_json = await res.json();
        const dt = new Date(match_json.date_time);  // ⬅️ parse ISO string

        // Format as YYYY-MM-DD and HH:MM for input elements
        matchForm.date.value = dt.toISOString().split("T")[0];

        const timeStr = dt.toTimeString().slice(0, 5);  // "HH:MM"
        matchForm.time.value = timeStr;

        matchForm.opponent.value = match_json.opponent || "";
        matchForm.court.value = match_json.court || "";
    }
};


function closeModal() {
    matchModal.style.display = "none";
}

matchForm.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(matchForm);
    const date = formData.get("date");
    const time = formData.get("time");
    const court = parseInt(formData.get("court"));
    const opponent = formData.get("opponent");

    const dateTime = new Date(`${date}T${time}:00`);

    const res = await fetch("/api/matches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            date: dateTime.toISOString(),
            court_number: court,
            opponent
        })
    });

    if (res.ok) {
        const data = await res.json();
        currentMatchId = data.match_id;
        closeModal();
        newGameBtn.disabled = false;
        statsMap = {};
        // Save match ID somewhere if needed
    }

    document.getElementById("matchDate").textContent = new Date(dateTime).toLocaleString();
    document.getElementById("matchCourt").textContent = court;
    document.getElementById("matchOpponent").textContent = opponent || "—";

    document.getElementById("game1Result").textContent = "—";
    document.getElementById("game2Result").textContent = "—";
    document.getElementById("game3Result").textContent = "—";

    currentGameNumber = 0;

    document.getElementById("currentGameNumber").textContent = "—";

    document.querySelectorAll("#playerStatsGrid select").forEach(sel => {
        sel.selectedIndex = 0;
    });


};

const gameScoreModal = document.getElementById("gameScoreModal");
const gameScoreForm = document.getElementById("gameScoreForm");

function closeGameModal() {
    gameScoreModal.style.display = "none";
}

let endMatch = false;

newGameBtn.onclick = () => {
    if (currentGameNumber > 0 && lastGameId) {
        // Clear previous inputs
        gameScoreForm.score.value = "";
        gameScoreForm.score_opponent.value = "";
        endMatch = false;
        // Show modal
        gameScoreModal.style.display = "flex";
    } else {
        createNewGame();
    }
};



endMatchBtn.onclick = () => {
    endMatch = true;
    gameScoreModal.style.display = "flex";
}

gameScoreForm.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(gameScoreForm);
    const score = parseInt(formData.get("score"));
    const scoreOpponent = parseInt(formData.get("score_opponent"));

    // Update last game with score
    await fetch(`/api/games/${lastGameId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ score, score_opponent: scoreOpponent, end_time: new Date().toISOString() })
    });

    if (endMatch) {
        await fetch(`/api/match/${currentMatchId}/end`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ end_time: new Date().toISOString() })
        });

        const selectedPlayerIds = Array.from(document.querySelectorAll("#playerStatsGrid select"))
            .map(sel => sel.value)
            .filter(val => val);  // ignore "None"

        // First assign players to the game
        await fetch(`/api/games/${lastGameId}/players`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ players: selectedPlayerIds })
        });


    }

    const gamescores =
        [
            document.getElementById("game1Result"),
            document.getElementById("game2Result"),
            document.getElementById("game3Result"),
        ];

    if (currentGameNumber <= 3)
        gamescores[currentGameNumber - 1].textContent = score + "-" + scoreOpponent;

    closeGameModal();
    //if (currentGameNumber <= 3)
    if (!endMatch)
        createNewGame();
};


async function createNewGame() {
    const res = await fetch("/api/games", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            match_id: currentMatchId,
            game_number: currentGameNumber + 1,
            start_time: new Date().toISOString()
        })
    });

    if (res.ok) {
        const game = await res.json();
        currentGameNumber = game.game_number;
        lastGameId = game.id;

        const selectedPlayerIds = Array.from(document.querySelectorAll("#playerStatsGrid select"))
            .map(sel => sel.value)
            .filter(val => val);  // ignore "None"

        // First assign players to the game
        await fetch(`/api/games/${game.id}/players`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ players: selectedPlayerIds })
        });

        // THEN fetch stats (so backend knows who the players are)
        const statsRes = await fetch(`/api/stats/${currentMatchId}/${currentGameNumber}`);
        if (statsRes.ok) {
            statsMap = {};  // Clear previous game data
            statsMap = await statsRes.json();

            // Refresh display
            document.querySelectorAll("#playerStatsGrid select").forEach(sel => {
                sel.dispatchEvent(new Event("change"));
            });
        }

        document.getElementById("currentGameNumber").textContent = game.game_number;
    }
}


