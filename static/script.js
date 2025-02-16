/***********************************************************
 * SCRIPT.JS - Cognitive Games with Holistic Scoring, In-Depth Risk Assessment, and Personalization
 ***********************************************************/

/* ------------------ NAVIGATION & PERSONALIZATION ------------------ */
function navigateTo(sectionId) {
  hideAllSections();
  document.getElementById(sectionId).classList.remove("hidden");
  startGame(sectionId);
  updateCognitivePerformanceBar();
}

function goHome() {
  hideAllSections();
  document.getElementById("home-screen").classList.remove("hidden");
  updateCognitivePerformanceBar();
}

function hideAllSections() {
  document.querySelectorAll("section.card").forEach(sec => sec.classList.add("hidden"));
}

// Personalization: Save and load user name
function loadUserName() {
  return localStorage.getItem("userName") || "";
}

function saveUserName(name) {
  localStorage.setItem("userName", name);
  updateWelcomeMessage();
}

function updateWelcomeMessage() {
  let name = loadUserName();
  let welcomeEl = document.getElementById("welcome-message");
  welcomeEl.textContent = name ? `Welcome, ${name}! Embark on your cognitive journey.` : "Embark on your cognitive journey.";
}

document.getElementById("save-name-btn").addEventListener("click", function () {
  let nameInput = document.getElementById("username-input").value;
  saveUserName(nameInput);
});

/* ------------------ DATA STORAGE & PERFORMANCE ------------------ */
function loadResults() {
  let data = localStorage.getItem("gameResults");
  return data ? JSON.parse(data) : [];
}

function saveResult(gameType, score) {
  let results = loadResults();
  results.push({
    id: crypto.randomUUID(),
    gameType,
    score, // 0–100
    timestamp: Date.now()
  });
  localStorage.setItem("gameResults", JSON.stringify(results));
}

const gameWeights = {
  memory: 1.5,
  reaction: 1.0,
  stroop: 1.2,
  sequence: 1.3,
  math: 1.0,
  scramble: 0.8,
  pattern: 1.0,
  visualSearch: 1.1,
  rotation: 0.9,
  numberRecall: 1.0
};

function average(arr) {
  return arr.length ? arr.reduce((sum, v) => sum + v, 0) / arr.length : 0;
}

function computeOverallPerformance() {
  let results = loadResults();
  if (results.length === 0) return 0;
  
  let grouped = {};
  let totalWeight = 0;
  let weightedSum = 0;
  results.forEach(r => {
    if (!grouped[r.gameType]) grouped[r.gameType] = [];
    grouped[r.gameType].push(r.score);
  });
  for (let g in gameWeights) {
    if (grouped[g] && grouped[g].length > 0) {
      let avgScore = average(grouped[g]);
      weightedSum += avgScore * gameWeights[g];
      totalWeight += gameWeights[g];
    }
  }
  return totalWeight > 0 ? weightedSum / totalWeight : 0;
}

/* ------------------ IN-DEPTH RISK ASSESSMENT ------------------ */
function computeRiskAssessments() {
  let results = loadResults();
  let grouped = {};
  results.forEach(r => {
    if (!grouped[r.gameType]) grouped[r.gameType] = [];
    grouped[r.gameType].push(r.score);
  });
  
  let avgMemory = grouped["memory"] ? average(grouped["memory"]) : 100;
  let avgReaction = grouped["reaction"] ? average(grouped["reaction"]) : 100;
  let avgStroop = grouped["stroop"] ? average(grouped["stroop"]) : 100;
  let avgSequence = grouped["sequence"] ? average(grouped["sequence"]) : 100;
  let avgMath = grouped["math"] ? average(grouped["math"]) : 100;
  let avgScramble = grouped["scramble"] ? average(grouped["scramble"]) : 100;
  let avgPattern = grouped["pattern"] ? average(grouped["pattern"]) : 100;
  let avgVisual = grouped["visualSearch"] ? average(grouped["visualSearch"]) : 100;
  let avgRotation = grouped["rotation"] ? average(grouped["rotation"]) : 100;
  let avgNumber = grouped["numberRecall"] ? average(grouped["numberRecall"]) : 100;
  
  // Alzheimer’s risk: Memory, Number Recall, Visual Search
  let alzMetric = (avgMemory * 0.4 + avgNumber * 0.3 + avgVisual * 0.3);
  let alzRisk = (alzMetric >= 80 ? "Low" : alzMetric >= 60 ? "Moderate" : "High");
  
  // Parkinson’s risk: Reaction, Rotation, Pattern
  let parkMetric = (avgReaction * 0.4 + avgRotation * 0.4 + avgPattern * 0.2);
  let parkRisk = (parkMetric >= 80 ? "Low" : parkMetric >= 60 ? "Moderate" : "High");
  
  // FTD risk: Stroop, Scramble, Sequence
  let ftdMetric = (avgStroop * 0.4 + avgScramble * 0.3 + avgSequence * 0.3);
  let ftdRisk = (ftdMetric >= 85 ? "Low" : ftdMetric >= 65 ? "Moderate" : "High");
  
  // MCI risk: Math, Memory
  let mciMetric = (avgMath * 0.5 + avgMemory * 0.5);
  let mciRisk = (mciMetric >= 90 ? "Low" : mciMetric >= 70 ? "Moderate" : "High");
  
  return {
    alzheimers: alzRisk,
    parkinsons: parkRisk,
    ftd: ftdRisk,
    mci: mciRisk
  };
}

function updateCognitivePerformanceBar() {
  let overall = computeOverallPerformance();
  let barFill = document.getElementById("trend-bar-fill");
  let barLabel = document.getElementById("trend-bar-label");
  
  barLabel.textContent = `Cognitive Performance: ${overall.toFixed(1)}`;
  barFill.style.width = overall + "%";
  if (overall < 40) barFill.style.background = "#D32F2F"; // Red
  else if (overall < 70) barFill.style.background = "#FFB6C1"; // Pink
  else barFill.style.background = "#81D4FA"; // Blue
  
  let risks = computeRiskAssessments();
  document.getElementById("alzheimers-risk").textContent = "Alzheimer’s Risk: " + risks.alzheimers;
  document.getElementById("parkinsons-risk").textContent = "Parkinson’s Risk: " + risks.parkinsons;
  document.getElementById("ftd-risk").textContent = "FTD Risk: " + risks.ftd;
  document.getElementById("mci-risk").textContent = "MCI Risk: " + risks.mci;
}

function resetCognitivePerformance() {
  localStorage.removeItem("gameResults");
  updateCognitivePerformanceBar();
}

/* ------------------ HELPER: Combine Time & Accuracy ------------------ */
function combineTimeAccuracy(accuracyFactor, timeFactor, accuracyWeight = 0.5) {
  let combined = accuracyWeight * accuracyFactor + (1 - accuracyWeight) * timeFactor;
  combined = Math.max(0, Math.min(1, combined));
  return combined * 100;
}

/* ------------------ GAME STARTER ------------------ */
function startGame(sectionId) {
  switch (sectionId) {
    case "memory-game": startMemoryGame(); break;
    case "reaction-game": startReactionGame(); break;
    case "stroop-game": startStroopGame(); break;
    case "sequence-game": startSequenceGame(); break;
    case "math-game": startMathGame(); break;
    case "scramble-game": startScrambleGame(); break;
    case "pattern-game": startPatternGame(); break;
    case "visual-game": startVisualGame(); break;
    case "rotation-game": startRotationGame(); break;
    case "number-game": startNumberGame(); break;
    default: break;
  }
}

/* ------------------ 1) MEMORY GAME ------------------ */
let memoryWords = ["apple", "banana", "cat", "dog", "house", "car", "music", "sun", "river", "book", "piano", "desk"];
let memoryCurrent = [];
let memoryStartTime = 0;
let memoryDisplayTimeMS = 4000;

function startMemoryGame() {
  document.getElementById("memory-words").textContent = "";
  document.getElementById("memory-answer").value = "";
  document.getElementById("memory-score").classList.add("hidden");
  document.getElementById("memory-analysis").textContent = "";
  document.getElementById("memory-answer-section").classList.add("hidden");

  memoryCurrent = shuffle(memoryWords).slice(0, 4);
  document.getElementById("memory-words").textContent = memoryCurrent.join(", ");
  setTimeout(() => {
    document.getElementById("memory-words").textContent = "";
    document.getElementById("memory-answer-section").classList.remove("hidden");
    memoryStartTime = performance.now();
  }, memoryDisplayTimeMS);
}

function checkMemoryAnswer() {
  let endTime = performance.now();
  let timeUsed = (endTime - memoryStartTime) / 1000;
  let userInput = document.getElementById("memory-answer").value.toLowerCase();
  let userArr = userInput.split(",").map(x => x.trim());
  let correctArr = memoryCurrent.map(x => x.toLowerCase());
  let correctCount = userArr.filter(x => correctArr.includes(x)).length;
  let accuracyFactor = correctCount / correctArr.length;
  let expectedTime = 10;
  let timeFactor = Math.min(1, expectedTime / timeUsed);
  let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.6);

  document.getElementById("memory-score").textContent = `Score: ${finalScore.toFixed(1)}`;
  document.getElementById("memory-score").classList.remove("hidden");
  saveResult("memory", finalScore);
  updateCognitivePerformanceBar();

  let msg = (finalScore >= 90) ? "Excellent memory performance!" :
            (finalScore >= 70) ? "Good, but try to be quicker." :
            (finalScore >= 50) ? "Fair; some words missed or too slow." :
                                "Poor recall; potential red flag.";
  document.getElementById("memory-analysis").textContent = msg;

  if (finalScore >= 80) memoryDisplayTimeMS = Math.max(memoryDisplayTimeMS - 500, 2000);
  else if (finalScore < 50) memoryDisplayTimeMS = Math.min(memoryDisplayTimeMS + 500, 8000);

  setTimeout(startMemoryGame, 2000);
}

/* ------------------ 2) REACTION TIME ------------------ */
let reactionStart = 0;
function startReactionGame() {
  let promptEl = document.getElementById("reaction-prompt");
  let btnEl = document.getElementById("reaction-btn");
  let resultEl = document.getElementById("reaction-result");
  promptEl.textContent = "Wait...";
  btnEl.disabled = true;
  resultEl.classList.add("hidden");
  document.getElementById("reaction-analysis").textContent = "";
  
  let container = document.getElementById("reaction-container");
  let maxX = container.clientWidth - btnEl.clientWidth;
  let maxY = container.clientHeight - btnEl.clientHeight;
  let randX = Math.random() * maxX;
  let randY = Math.random() * maxY;
  btnEl.style.left = randX + "px";
  btnEl.style.top = randY + "px";
  
  let delay = Math.random() * 2000 + 2000;
  setTimeout(() => {
    promptEl.textContent = "Tap Now!";
    btnEl.disabled = false;
    reactionStart = performance.now();
  }, delay);
}

function handleReactionClick() {
  if (!reactionStart) return;
  let end = performance.now();
  let elapsed = end - reactionStart;
  document.getElementById("reaction-prompt").textContent = "Done!";
  let resultEl = document.getElementById("reaction-result");
  resultEl.classList.remove("hidden");
  resultEl.textContent = `Time: ${elapsed.toFixed(0)} ms`;
  
  let minAllowed = 200, maxAllowed = 1200;
  let factor = 1 - ((elapsed - minAllowed) / (maxAllowed - minAllowed));
  factor = Math.max(0, Math.min(1, factor));
  let finalScore = factor * 100;
  
  saveResult("reaction", finalScore);
  updateCognitivePerformanceBar();
  
  let msg = (finalScore >= 90) ? "Lightning-fast reaction!" :
            (finalScore >= 70) ? "Adequate speed." :
            (finalScore >= 50) ? "Some delay, possibly normal." :
                                "Very slow; could be a concern.";
  document.getElementById("reaction-analysis").textContent = msg;
  document.getElementById("reaction-btn").disabled = true;
  setTimeout(startReactionGame, 2000);
}

/* ------------------ 3) STROOP TEST ------------------ */
let stroopColors = ["Red", "Green", "Blue", "Yellow"];
let stroopTarget = null;
let stroopCorrect = 0;
let stroopAttempts = 0;
let stroopStartTime = 0;
function startStroopGame() {
  stroopCorrect = 0;
  stroopAttempts = 0;
  document.getElementById("stroop-score").textContent = `Score: 0`;
  document.getElementById("stroop-analysis").textContent = "";
  stroopStartTime = performance.now();
  generateStroop();
}
function generateStroop() {
  let wordEl = document.getElementById("stroop-word");
  let btnContainer = document.getElementById("stroop-buttons");
  btnContainer.innerHTML = "";
  let text = randomItem(stroopColors);
  let color = randomItem(stroopColors);
  stroopTarget = color;
  wordEl.textContent = text;
  wordEl.style.color = color.toLowerCase();
  stroopColors.forEach(c => {
    let btn = document.createElement("button");
    btn.textContent = c;
    btn.style.backgroundColor = c.toLowerCase();
    btn.onclick = () => checkStroopAnswer(c);
    btnContainer.appendChild(btn);
  });
}
function checkStroopAnswer(chosenColor) {
  stroopAttempts++;
  if (chosenColor === stroopTarget) stroopCorrect++;
  if (stroopAttempts >= 5) {
    let totalTime = (performance.now() - stroopStartTime) / 1000;
    let accuracyFactor = stroopCorrect / 5;
    let expectedTime = 15;
    let timeFactor = Math.min(1, expectedTime / totalTime);
    let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.5);
    document.getElementById("stroop-score").textContent = `Score: ${finalScore.toFixed(1)}`;
    saveResult("stroop", finalScore);
    updateCognitivePerformanceBar();
    let msg = (finalScore >= 90) ? "Excellent interference control!" :
              (finalScore >= 70) ? "Good performance." :
              (finalScore >= 50) ? "Fair; some interference issues." : "Poor performance.";
    document.getElementById("stroop-analysis").textContent = msg;
  } else {
    generateStroop();
  }
}

/* ------------------ 4) SEQUENCE MEMORY ------------------ */
let seqOrder = [];
let seqPos = 0;
let seqLevel = 0;
let seqStartTime = 0;
function startSequenceGame() {
  seqOrder = [];
  seqPos = 0;
  seqLevel = 0;
  buildSequenceGrid();
  document.getElementById("sequence-level").textContent = "";
  document.getElementById("sequence-analysis").textContent = "";
  seqStartTime = performance.now();
  nextSeqLevel();
}
function buildSequenceGrid() {
  let grid = document.getElementById("sequence-grid");
  grid.innerHTML = "";
  for (let i = 0; i < 9; i++) {
    let btn = document.createElement("button");
    btn.textContent = (i + 1);
    btn.onclick = (e) => {
      e.target.classList.add("clicked");
      setTimeout(() => { e.target.classList.remove("clicked"); }, 200);
      handleSequenceClick(i);
    };
    grid.appendChild(btn);
  }
}
function nextSeqLevel() {
  seqLevel++;
  seqPos = 0;
  document.getElementById("sequence-level").textContent = `Level: ${seqLevel}`;
  seqOrder.push(Math.floor(Math.random() * 9));
  showSequence();
}
function showSequence() {
  let i = 0;
  let grid = document.getElementById("sequence-grid").children;
  function highlight() {
    let idx = seqOrder[i];
    let btn = grid[idx];
    let orig = btn.style.backgroundColor;
    btn.style.backgroundColor = "#ffafcc";
    setTimeout(() => {
      btn.style.backgroundColor = orig || "";
      i++;
      if (i < seqOrder.length) setTimeout(highlight, 500);
    }, 500);
  }
  setTimeout(highlight, 700);
}
function handleSequenceClick(idx) {
  if (idx === seqOrder[seqPos]) {
    seqPos++;
    if (seqPos === seqOrder.length) {
      let accuracyFactor = 1;
      let totalTime = (performance.now() - seqStartTime) / 1000;
      let expectedTime = 60;
      let timeFactor = Math.min(1, expectedTime / totalTime);
      let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.7);
      saveResult("sequence", finalScore);
      document.getElementById("sequence-analysis").textContent =
        `Perfect recall at level ${seqLevel}. Score: ${finalScore.toFixed(1)}`;
      updateCognitivePerformanceBar();
      setTimeout(nextSeqLevel, 1000);
    }
  } else {
    let accuracyFactor = seqPos / seqOrder.length;
    let totalTime = (performance.now() - seqStartTime) / 1000;
    let expectedTime = 60;
    let timeFactor = Math.min(1, expectedTime / totalTime);
    let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.7);
    saveResult("sequence", finalScore);
    document.getElementById("sequence-analysis").textContent =
      `You got ${seqPos} out of ${seqOrder.length}. Score: ${finalScore.toFixed(1)}`;
    updateCognitivePerformanceBar();
    setTimeout(startSequenceGame, 1500);
  }
}

/* ------------------ 5) MATH GAME ------------------ */
let mathAnswer = 0;
let mathStartTime = 0;
function startMathGame() {
  document.getElementById("math-answer").value = "";
  document.getElementById("math-result").classList.add("hidden");
  document.getElementById("math-analysis").textContent = "";
  
  let a = Math.floor(Math.random() * 10) + 1;
  let b = Math.floor(Math.random() * 10) + 1;
  let op = randomItem(["+", "-", "*"]);
  mathAnswer = eval(`${a} ${op} ${b}`);
  document.getElementById("math-problem").textContent = `${a} ${op} ${b} = ?`;
  mathStartTime = performance.now();
}

function checkMathAnswer() {
  let userVal = parseFloat(document.getElementById("math-answer").value);
  let totalTime = (performance.now() - mathStartTime) / 1000;
  let correct = (userVal === mathAnswer) ? 1 : 0;
  let accuracyFactor = correct;
  let expected = 5;
  let timeFactor = Math.min(1, expected / totalTime);
  let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.5);
  
  if (correct === 1)
    document.getElementById("math-result").textContent = `Correct! Score: ${finalScore.toFixed(1)}`;
  else
    document.getElementById("math-result").textContent = `Incorrect. Answer was ${mathAnswer}. Score: ${finalScore.toFixed(1)}`;
  
  document.getElementById("math-result").classList.remove("hidden");
  saveResult("math", finalScore);
  updateCognitivePerformanceBar();
  
  let msg = (finalScore >= 90) ? "Excellent math performance!" :
            (finalScore >= 70) ? "Decent, but try to be faster." :
            (finalScore >= 50) ? "Fair; could be improved." : "Struggled with math.";
  document.getElementById("math-analysis").textContent = msg;
  
  setTimeout(startMathGame, 2000);
}

/* ------------------ 6) WORD SCRAMBLE ------------------ */
let scrambleOriginal = "";
let scrambleStartTime = 0;
function startScrambleGame() {
  document.getElementById("scramble-result").classList.add("hidden");
  document.getElementById("scramble-analysis").textContent = "";
  document.getElementById("scramble-answer").value = "";
  
  let words = ["flower", "candle", "stream", "planet", "guitar", "window"];
  scrambleOriginal = randomItem(words);
  let scrambled = shuffle(scrambleOriginal.split("")).join("");
  document.getElementById("scramble-letters").textContent = scrambled;
  scrambleStartTime = performance.now();
}

function checkScrambleAnswer() {
  let totalTime = (performance.now() - scrambleStartTime) / 1000;
  let userGuess = document.getElementById("scramble-answer").value.trim().toLowerCase();
  let correct = (userGuess === scrambleOriginal.toLowerCase()) ? 1 : 0;
  let accuracyFactor = correct;
  let expected = 10;
  let timeFactor = Math.min(1, expected / totalTime);
  let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.6);
  
  if (correct === 1)
    document.getElementById("scramble-result").textContent = `Correct! Score: ${finalScore.toFixed(1)}`;
  else
    document.getElementById("scramble-result").textContent = `Incorrect. The word was "${scrambleOriginal}". Score: ${finalScore.toFixed(1)}`;
  
  document.getElementById("scramble-result").classList.remove("hidden");
  saveResult("scramble", finalScore);
  updateCognitivePerformanceBar();
  
  let msg = (finalScore >= 90) ? "Excellent unscrambling!" :
            (finalScore >= 70) ? "Good, but try to be quicker." :
            (finalScore >= 50) ? "Fair performance." : "Struggled with the scramble.";
  document.getElementById("scramble-analysis").textContent = msg;
}

/* ------------------ 7) PATTERN MATCH ------------------ */
let patternMatrix = [];
let patternStartTime = 0;
const PATTERN_SIZE = 25;
function startPatternGame() {
  document.getElementById("pattern-result").classList.add("hidden");
  document.getElementById("pattern-analysis").textContent = "";
  buildPatternGrid();
  patternMatrix = Array(PATTERN_SIZE).fill(false);
  for (let i = 0; i < 5; i++) {
    patternMatrix[Math.floor(Math.random() * PATTERN_SIZE)] = true;
  }
  flashPattern();
  patternStartTime = performance.now();
}

function buildPatternGrid() {
  let grid = document.getElementById("pattern-grid");
  grid.innerHTML = "";
  for (let i = 0; i < PATTERN_SIZE; i++) {
    let btn = document.createElement("button");
    btn.dataset.index = i;
    btn.onclick = (e) => {
      e.target.classList.add("clicked");
      setTimeout(() => { e.target.classList.remove("clicked"); }, 200);
      e.target.classList.toggle("active");
    };
    grid.appendChild(btn);
  }
}

function flashPattern() {
  let grid = document.getElementById("pattern-grid").children;
  for (let i = 0; i < PATTERN_SIZE; i++) {
    if (patternMatrix[i]) grid[i].style.background = "#FFB6C1";
  }
  setTimeout(() => {
    for (let i = 0; i < PATTERN_SIZE; i++) {
      grid[i].style.background = "";
    }
  }, 1500);
}

function checkPattern() {
  let endTime = performance.now();
  let totalTime = (endTime - patternStartTime) / 1000;
  let grid = document.getElementById("pattern-grid").children;
  let correctCount = 0;
  for (let i = 0; i < PATTERN_SIZE; i++) {
    let active = grid[i].classList.contains("active");
    if (active === patternMatrix[i]) correctCount++;
  }
  let accuracyFactor = correctCount / PATTERN_SIZE;
  let expected = 15;
  let timeFactor = Math.min(1, expected / totalTime);
  let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.7);
  
  document.getElementById("pattern-result").textContent = `Score: ${finalScore.toFixed(1)}`;
  document.getElementById("pattern-result").classList.remove("hidden");
  saveResult("pattern", finalScore);
  updateCognitivePerformanceBar();
  
  let msg = (finalScore >= 90) ? "Excellent pattern recall!" :
            (finalScore >= 70) ? "Good, with slight errors." :
            (finalScore >= 50) ? "Fair; try to improve consistency." : "Poor pattern reproduction.";
  document.getElementById("pattern-analysis").textContent = msg;
  
  setTimeout(startPatternGame, 2000);
}

/* ------------------ 8) VISUAL SEARCH ------------------ */
let visualRound = 1;
let visualStartTime = 0;
let visualTimer = null;
function startVisualGame() {
  document.getElementById("visual-result").classList.add("hidden");
  document.getElementById("visual-analysis").textContent = "";
  document.getElementById("visual-field").innerHTML = "";
  document.getElementById("visual-timer").textContent = "";
  document.getElementById("visual-round").textContent = `Round: ${visualRound}`;
  
  let gridSize = 3 + visualRound;
  let totalSquares = gridSize * gridSize;
  let targetIndex = Math.floor(Math.random() * totalSquares);
  
  for (let i = 0; i < totalSquares; i++) {
    let div = document.createElement("div");
    div.textContent = (i === targetIndex) ? "X" : "O";
    div.onclick = () => handleVisualClick(i === targetIndex);
    document.getElementById("visual-field").appendChild(div);
  }
  
  visualStartTime = performance.now();
  visualTimer = requestAnimationFrame(updateVisualTimer);
}

function updateVisualTimer() {
  let now = performance.now();
  let elapsed = (now - visualStartTime) / 1000;
  document.getElementById("visual-timer").textContent = `Time: ${elapsed.toFixed(1)}s`;
  visualTimer = requestAnimationFrame(updateVisualTimer);
}

function handleVisualClick(isTarget) {
  if (!isTarget) return;
  cancelAnimationFrame(visualTimer);
  let end = performance.now();
  let timeUsed = (end - visualStartTime) / 1000;
  let allowed = 3 - Math.min((visualRound - 1) * 0.2, 2.0);
  if (allowed < 1) allowed = 1;
  let timeFactor = Math.min(1, allowed / timeUsed);
  let finalScore = combineTimeAccuracy(1, timeFactor, 0.5);
  
  document.getElementById("visual-result").textContent =
    `Found in ${timeUsed.toFixed(1)}s, Score: ${finalScore.toFixed(1)}`;
  document.getElementById("visual-result").classList.remove("hidden");
  saveResult("visualSearch", finalScore);
  updateCognitivePerformanceBar();
  
  let msg = (finalScore >= 90) ? "Excellent search performance!" :
            (finalScore >= 70) ? "Good, with minor delay." :
            (finalScore >= 50) ? "Fair; could be improved." : "Poor search performance.";
  document.getElementById("visual-analysis").textContent = msg;
  
  visualRound++;
  setTimeout(startVisualGame, 2000);
}

/* ------------------ 9) SPATIAL ROTATION ------------------ */
let rotationIsSame = false;
let rotationStartTime = 0;
let rotationOriginal = "";
function startRotationGame() {
  document.getElementById("rotation-result").classList.add("hidden");
  document.getElementById("rotation-analysis").textContent = "";
  let origDiv = document.getElementById("rotation-original");
  let dispDiv = document.getElementById("rotation-display");
  origDiv.textContent = "";
  dispDiv.textContent = "";
  
  let letters = ["F", "G", "L", "P", "R", "E"];
  rotationOriginal = randomItem(letters);
  origDiv.textContent = rotationOriginal;
  origDiv.style.transform = "none";
  
  setTimeout(() => {
    rotationIsSame = (Math.random() < 0.5);
    let deg = [0, 90, 180, 270][Math.floor(Math.random() * 4)];
    dispDiv.textContent = rotationOriginal;
    if (rotationIsSame)
      dispDiv.style.transform = `rotate(${deg}deg)`;
    else
      dispDiv.style.transform = `rotate(${deg}deg) scaleX(-1)`;
    rotationStartTime = performance.now();
  }, 2000);
}

function rotationCheck(userSaysSame) {
  let end = performance.now();
  let timeUsed = (end - rotationStartTime) / 1000;
  let correct = (userSaysSame === rotationIsSame) ? 1 : 0;
  let accuracyFactor = correct;
  let expected = 5;
  let timeFactor = Math.min(1, expected / timeUsed);
  let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.6);
  
  if (correct === 1)
    document.getElementById("rotation-result").textContent = `Correct! Score: ${finalScore.toFixed(1)}`;
  else
    document.getElementById("rotation-result").textContent = `Incorrect! Score: ${finalScore.toFixed(1)}`;
  
  document.getElementById("rotation-result").classList.remove("hidden");
  saveResult("rotation", finalScore);
  updateCognitivePerformanceBar();
  
  let msg = (finalScore >= 90) ? "Excellent spatial judgment!" :
            (finalScore >= 70) ? "Good." :
            (finalScore >= 50) ? "Fair; some errors." : "Poor spatial processing.";
  document.getElementById("rotation-analysis").textContent = msg;
}

/* ------------------ 10) NUMBER RECALL ------------------ */
let numberCorrect = "";
let numberStartTime = 0;
let numberDisplayTimeMS = 3000;
function startNumberGame() {
  document.getElementById("number-flash").textContent = "";
  document.getElementById("number-answer").value = "";
  document.getElementById("number-result").classList.add("hidden");
  document.getElementById("number-analysis").textContent = "";
  document.getElementById("number-answer-section").classList.add("hidden");

  let len = Math.floor(Math.random() * 3) + 5;
  let digits = "";
  for (let i = 0; i < len; i++) {
    digits += Math.floor(Math.random() * 10);
  }
  numberCorrect = digits;
  document.getElementById("number-flash").textContent = digits;
  setTimeout(() => {
    document.getElementById("number-flash").textContent = "";
    document.getElementById("number-answer-section").classList.remove("hidden");
    numberStartTime = performance.now();
  }, numberDisplayTimeMS);
}

function checkNumberRecall() {
  let end = performance.now();
  let timeUsed = (end - numberStartTime) / 1000;
  let userAns = document.getElementById("number-answer").value;
  let correct = (userAns === numberCorrect) ? 1 : 0;
  let accuracyFactor = correct;
  let expected = 10;
  let timeFactor = Math.min(1, expected / timeUsed);
  let finalScore = combineTimeAccuracy(accuracyFactor, timeFactor, 0.7);
  
  if (correct === 1)
    document.getElementById("number-result").textContent = `Correct! Score: ${finalScore.toFixed(1)}`;
  else
    document.getElementById("number-result").textContent = `Incorrect. Correct: ${numberCorrect}. Score: ${finalScore.toFixed(1)}`;
  
  document.getElementById("number-result").classList.remove("hidden");
  saveResult("numberRecall", finalScore);
  updateCognitivePerformanceBar();
  
  let msg = (finalScore >= 90) ? "Perfect recall!" :
            (finalScore >= 70) ? "Good retention." :
            (finalScore >= 50) ? "Fair memory." : "Poor recall.";
  document.getElementById("number-analysis").textContent = msg;
  
  if (finalScore >= 80)
    numberDisplayTimeMS = Math.max(numberDisplayTimeMS - 500, 1000);
  else
    numberDisplayTimeMS = Math.min(numberDisplayTimeMS + 500, 7000);
  
  setTimeout(startNumberGame, 2000);
}

/* ------------------ HELPERS ------------------ */
function shuffle(arr) {
  let a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    let j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}
