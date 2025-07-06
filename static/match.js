document.addEventListener("DOMContentLoaded", async () => {
  const statGroups = {
    Serve: ["Ace", "ServiceError"],
    Attack: ["Kill", "AttackError"],
    Block: ["Block"],
    Dig: ["Dig"],
    Reception: ["Reception", "ReceptionError"],
    Assist: ["Assist"],
    Touch: ["Touch"]
  };

  const statToString = {
    ServiceError : "Error",
    AttackError : "Error",
    ReceptionError : "Error",
    Touch : "Other Touch"
  }

  const grid = document.getElementById("playerStatsGrid");

  const players = await fetch("/api/players").then(res => res.json());
  const statsMap = {};
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
  

 players.forEach(player => {
  const row = document.createElement("tr");
  const row2 = document.createElement("tr");
  const stat = statsMap[player.id] || {};

  // Create and span player name cell
  const tdName = document.createElement("td");
  tdName.textContent = `#${player.jersey} ${player.name}`;
  tdName.rowSpan = 2;
  row.appendChild(tdName);

  for (const group in statGroups) {
    let groupTotal = 0;

    statGroups[group].forEach(statName => {
      const td = document.createElement("td");

      const btn = document.createElement("button");
      btn.textContent = `${statToString[statName] || statName}: ${stat[statName] || 0}`;
      groupTotal += stat[statName] || 0;

      btn.onclick = async () => {
        const res = await fetch(`/api/stats/${player.id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ [statName]: 1 })
        });

        if (res.ok) {
          const updated = await res.json();
          btn.textContent = `${statToString[statName] || statName}: ${stat[statName] || 0}`;
          // update the total cell for this group
          totalCell.textContent = `Total: ${statGroups[group].reduce((sum, s) => (updated[s] || 0) + sum, 0)}`;
        }
      };

      td.appendChild(btn);
      row.appendChild(td);
    });

    // Now create total cell for that group in row2
    const totalCell = document.createElement("td");
    totalCell.colSpan = statGroups[group].length;
    totalCell.textContent = `Total: ${groupTotal}`;
    totalCell.style.fontWeight = "bold";
    totalCell.style.textAlign = "center";
    row2.appendChild(totalCell);
  }

  table.appendChild(row);
  table.appendChild(row2);
});


  grid.appendChild(table);
});
