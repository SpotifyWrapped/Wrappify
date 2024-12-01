const canvas = document.querySelector('canvas');
const c = canvas.getContext('2d');
canvas.width = 1024
canvas.height = 576
c.fillRect(0, 0, canvas.width, canvas.height)
const gravity = 0.7

// CLASSES //

// sprite
class Sprite {
    constructor({position, imageSrc, scale = 1, framesMax = 1, offset = {x: 0, y: 0}}) {
        this.position = position
        this.width = 50
        this.height = 150
        this.image = new Image()
        this.image.src = imageSrc
        this.scale = scale,
        this.framesMax = framesMax,
        this.framesCurrent = 0
        this.framesElapsed = 0
        this.framesHold = 5
        this.offset = offset
    }

    draw () {
        c.drawImage(this.image, this.framesCurrent * (this.image.width / this.framesMax), 0, this.image.width / this.framesMax, this.image.height, this.position.x - this.offset.x, this.position.y - this.offset.y, (this.image.width / this.framesMax) * this.scale, this.image.height * this.scale)
    }

    animateFrames() {
        this.framesElapsed++

        if (this.framesElapsed % this.framesHold === 0)
        if (this.framesCurrent < this.framesMax - 1) {
        this.framesCurrent++
        } else {
            this.framesCurrent = 0;
        }
    }

    update () {
        this.draw()
        this.animateFrames()
    }
}

// fighter
class Fighter extends Sprite {
    constructor({position, velocity, color = 'white', imageSrc, scale = 1, framesMax = 1, offset = {x: 0, y: 0}, sprites, attackBox = { offset: {}, width: undefined, height: undefined }, attackCooldown = 0 }) {
        super({
            position,
            imageSrc,
            scale,
            framesMax,
            offset
        })

        this.velocity = velocity
        this.width = 50
        this.height = 150
        this.lastKey
        this.attackBox = {
            position: {
                x: this.position.x,
                y: this.position.y,
            },
            offset: attackBox.offset,
            width: attackBox.width,
            height: attackBox.height,
        }
        this.color = color
        this.isAttacking = false;
        this.health = 100
        this.framesCurrent = 0
        this.framesElapsed = 0
        this.framesHold = 5
        this.sprites = sprites
        this.dead = false
        this.lastAttackTime = 0;
        this.attackCooldown = attackCooldown;

        for (const sprite in this.sprites) {
            sprites[sprite].image = new Image()
            sprites[sprite].image.src = sprites[sprite].imageSrc
        }

        console.log(this.sprites)
    }

    update () {
        this.draw();
        if (!this.dead) this.animateFrames();

        this.attackBox.position.x = this.position.x + this.attackBox.offset.x;
        this.attackBox.position.y = this.position.y + this.attackBox.offset.y;

        // draw attack box
        // c.fillRect(this.attackBox.position.x, this.attackBox.position.y, this.attackBox.width, this.attackBox.height)


        this.position.x += this.velocity.x
        this.position.y += this.velocity.y

        // gravity
        if (this.position.y + this.height + this.velocity.y >= canvas.height - 70) {
            this.velocity.y = 0
            this.position.y = canvas.height - 70 - this.height;
        } else this.velocity.y += gravity
    }

    attack() {
        this.switchSprites('attack1');
        this.isAttacking = true;
        // Reset attacking state after animation
        setTimeout(() => {
            this.isAttacking = false;
        }, 500);  // Adjust this timeout based on animation length
    }

    takeHit() {
        this.health -= 20
        if (this.health <= 0) {
            this.switchSprites('death')
        } else this.switchSprites('takeHit')
    }

    switchSprites(sprite) {

        if (this.image === this.sprites.death.image) {
            if (this.framesCurrent === this.sprites.death.framesMax - 1)
                this.dead = true
            return
        }

        if (this.image == this.sprites.attack1.image && this.framesCurrent < this.sprites.attack1.framesMax - 1) return
        
        if (this.image === this.sprites.takeHit.image && this.framesCurrent < this.sprites.takeHit.framesMax - 1) return

        switch (sprite) {
            case 'idle':
                if (this.image !== this.sprites.idle.image) {
                    this.image = this.sprites.idle.image
                    this.framesMax = this.sprites.idle.framesMax
                    this.framesCurrent = 0
                }
                break
            case 'run':
                if (this.image !== this.sprites.run.image) {
                    this.image = this.sprites.run.image
                    this.framesMax = this.sprites.run.framesMax
                    this.framesCurrent = 0
                }
                break
            case 'jump':
                if (this.image !== this.sprites.jump.image) {
                    this.image = this.sprites.jump.image
                    this.framesMax = this.sprites.jump.framesMax
                    this.framesCurrent = 0
                }
                break
            case 'fall':
                if (this.image !== this.sprites.fall.image) {
                    this.image = this.sprites.fall.image
                    this.framesMax = this.sprites.fall.framesMax
                    this.framesCurrent = 0
                }
                break
            case 'attack1':
                if (this.image !== this.sprites.attack1.image) {
                    this.image = this.sprites.attack1.image
                    this.framesMax = this.sprites.attack1.framesMax
                    this.framesCurrent = 0
                }
                break
            case 'takeHit':
                if (this.image !== this.sprites.takeHit.image) {
                    this.image = this.sprites.takeHit.image
                    this.framesMax = this.sprites.takeHit.framesMax
                    this.framesCurrent = 0
                }
                break
            case 'death':
                if (this.image !== this.sprites.death.image) {
                    this.image = this.sprites.death.image
                    this.framesMax = this.sprites.death.framesMax
                    this.framesCurrent = 0
                }
                break
        }
    }
}

// INSTANCES //

// background
const background = new Sprite({
    position: {
        x: 0,
        y: 0,
    },
    imageSrc: backgroundImageSrc
})

// players

// huntress
// const player = new Fighter({
//     position: {
//         x: 150,
//         y: 0
//     },
//     velocity: {
//         x: 0,
//         y: 0
//     },
//     offset: {
//         x: 0,
//         y: 0
//     },
//     imageSrc: playerIdle,
//     framesMax: 8,
//     scale: 3,
//     offset: {
//         x: 215,
//         y: 136,
//     },
//     sprites: {
//         idle: {
//             imageSrc: playerIdle,
//             framesMax: 8
//         },
//         run: {
//             imageSrc: playerRun,
//             framesMax: 8
//         },
//         jump: {
//             imageSrc: playerJump,
//             framesMax: 2
//         },
//         fall: {
//             imageSrc: playerFall,
//             framesMax: 2
//         },
//         attack1: {
//             imageSrc: playerAttack1,
//             framesMax: 5
//         },
//         takeHit: {
//             imageSrc: playerHit,
//             framesMax: 3
//         },
//         death: {
//             imageSrc: playerDeath,
//             framesMax: 8
//         }
//     },
//     attackBox: {
//         offset: {
//             x: 40,
//             y: 50,
//         },
//         width: 130,
//         height: 50,
//     }
// })



// knight
const player = new Fighter({
    position: {
        x: 150,
        y: 0
    },
    velocity: {
        x: 0,
        y: 0
    },
    offset: {
        x: 0,
        y: 0
    },
    imageSrc: playerIdle,
    framesMax: 12,
    scale: 2.5,
    offset: {
        x: 215,
        y: 130,
    },
    sprites: {
        idle: {
            imageSrc: playerIdle,
            framesMax: 11
        },
        run: {
            imageSrc: playerRun,
            framesMax: 8

        },
        jump: {
            imageSrc: playerJump,
            framesMax: 3

        },
        fall: {
            imageSrc: playerFall,
            framesMax: 3
        },
        attack1: {
            imageSrc: playerAttack1,
            framesMax: 7
        },
        takeHit: {
            imageSrc: playerHit,
            framesMax: 4
        },
        death: {
            imageSrc: playerDeath,
            framesMax: 11
        }
    },
    attackBox: {
        offset: {
            x: 40,
            y: 50,
        },
        width: 180,
        height: 50,
    }
})

// lightning warrior
// const player = new Fighter({
//     position: {
//         x: 150,
//         y: 0
//     },
//     velocity: {
//         x: 0,
//         y: 0
//     },
//     offset: {
//         x: 0,
//         y: 0
//     },
//     imageSrc: playerIdle,
//     framesMax: 8,
//     scale: 2.7,
//     offset: {
//         x: 215,
//         y: 120,
//     },
//     sprites: {
//         idle: {
//             imageSrc: playerIdle,
//             framesMax: 10
//         },
//         run: {
//             imageSrc: playerRun,
//             framesMax: 8
//         },
//         jump: {
//             imageSrc: playerJump,
//             framesMax: 3
//         },
//         fall: {
//             imageSrc: playerFall,
//             framesMax: 3
//         },
//         attack1: {
//             imageSrc: playerAttack1,
//             framesMax: 8
//         },
//         takeHit: {
//             imageSrc: playerHit,
//             framesMax: 3
//         },
//         death: {
//             imageSrc: playerDeath,
//             framesMax: 7
//         }
//     },
//     attackBox: {
//         offset: {
//             x: 20,
//             y: 50,
//         },
//         width: 180,
//         height: 50,
//     }
// })



// enemy



// sword guy
// const enemy = new Fighter({
//     position: {
//         x: 850,
//         y: 100
//     },
//     velocity: {
//         x: 0,
//         y: 0,
//     },
//     offset: {
//         x: 0,
//         y: 0
//     },
//     color: 'blue',
//     imageSrc: enemyIdle,
//     framesMax: 8,
//     scale: 2.5,
//     offset: {
//         x: 215,
//         y: 167,
//     },
//     sprites: {
//         idle: {
//             imageSrc: enemyIdle,
//             framesMax: 4
//         },
//         run: {
//             imageSrc: enemyRun,
//             framesMax: 8
//         },
//         jump: {
//             imageSrc: enemyJump,
//             framesMax: 2
//         },
//         fall: {
//             imageSrc: enemyFall,
//             framesMax: 2
//         },
//         attack1: {
//             imageSrc: enemyAttack1,
//             framesMax: 4
//         },
//         takeHit: {
//             imageSrc: enemyHit,
//             framesMax: 3
//         },
//         death: {
//             imageSrc: enemyDeath,
//             framesMax: 7
//         }
//     },
//     attackBox: {
//         offset: {
//             x: -160,
//             y: 40,
//         },
//         width: 170,
//         height: 50,
//     },
//     attackCooldown: 6000
// })

// evil wizard
const enemy = new Fighter({
    position: {
        x: 850,
        y: 0
    },
    velocity: {
        x: 0,
        y: 0,
    },
    offset: {
        x: 0,
        y: 0
    },
    color: 'blue',

    imageSrc: enemyIdle,
    framesMax: 12,
    scale: 2.5,
    offset: {
        x: 215,
        y: 263,
    },
    sprites: {
        idle: {
            imageSrc: enemyIdle,
            framesMax: 8
        },
        run: {
            imageSrc: enemyRun,
            framesMax: 8

        },
        jump: {
            imageSrc: enemyJump,
            framesMax: 2

        },
        fall: {
            imageSrc: enemyFall,
            framesMax: 2
        },
        attack1: {
            imageSrc: enemyAttack1,
            framesMax: 8
        },
        takeHit: {
            imageSrc: enemyHit,
            framesMax: 3
        },
        death: {
            imageSrc: enemyDeath,
            framesMax: 7
        },
    },
    attackBox: {
        offset: {
            x: -160,
            y: 40,
        },
        width: 190,
        height: 50,
    },
    attackCooldown: 6000
})

// girl wizard
// const enemy = new Fighter({
//     position: {
//         x: 850,
//         y: 100
//     },
//     velocity: {
//         x: 0,
//         y: 0,
//     },
//     offset: {
//         x: 0,
//         y: 0
//     },
//     color: 'blue',
//     imageSrc: enemyIdle,
//     framesMax: 18,
//     scale: 2.5,
//     offset: {
//         x: 215,
//         y: 90,
//     },
//     sprites: {
//         idle: {
//             imageSrc: enemyIdle,
//             framesMax: 10
//         },
//         run: {
//             imageSrc: enemyRun,
//             framesMax: 8
//         },
//         jump: {
//             imageSrc: enemyJump,
//             framesMax: 3
//         },
//         fall: {
//             imageSrc: enemyFall,
//             framesMax: 3
//         },
//         attack1: {
//             imageSrc: enemyAttack1,
//             framesMax: 13
//         },
//         takeHit: {
//             imageSrc: enemyHit,
//             framesMax: 3
//         },
//         death: {
//             imageSrc: enemyDeath,
//             framesMax: 18
//         },
//     },
//     attackBox: {
//         offset: {
//             x: -250,
//             y: 40,
//         },
//         width: 190,
//         height: 50,
//     },
//     attackCooldown: 6000
// })


console.log(player)

const keys = {
    a: {
        pressed: false
    },
    d: {
        pressed: false
    },
    w: {
        pressed: false
    },
    ArrowRight: {
        pressed: false
    },
    ArrowLeft: {
        pressed: false
    },
}


// FUNTIONS //

function rectangularCollision({rectangle1, rectangle2}) {
    return (
        rectangle1.attackBox.position.x + rectangle1.attackBox.width >= rectangle2.position.x &&
        rectangle1.attackBox.position.x <= rectangle2.position.x + rectangle2.width &&
        rectangle1.attackBox.position.y + rectangle1.attackBox.height >= rectangle2.position.y &&
        rectangle1.attackBox.position.y <= rectangle2.position.y + rectangle2.height
    )
}

// Enemy attack function with cooldown logic
enemy.attack = function () {
    if (!this.isAttacking && (Date.now() - this.lastAttackTime > this.attackCooldown)) {
        // Call the original attack logic
        Fighter.prototype.attack.call(this);
        
        // Set cooldown specifics
        this.lastAttackTime = Date.now();  
    }
}

function enemyAI() {
    // Check if enemy is dead before performing any AI actions
    if (enemy.dead) {
        enemy.velocity.x = 0; // Stop any movement
        return; // Exit the function if the enemy is dead
    }

    const distanceToPlayer = Math.abs(player.position.x - enemy.position.x);

    // Move towards player if not close enough to attack
    if (distanceToPlayer > enemy.attackBox.width) {
        if (player.position.x < enemy.position.x) {
            enemy.velocity.x = -2;  // Move left towards player
            enemy.switchSprites('run');
        } else {
            enemy.velocity.x = 4;  // Move right towards player
            enemy.switchSprites('run');
        }
    } else {
        enemy.velocity.x = 0;
        enemy.switchSprites('idle');

        // Attack if close enough and player is not dead
        if (!enemy.isAttacking && !player.dead) {
            enemy.attack();
        }
    }

    // Randomly jump occasionally to make it more dynamic
    if (!enemy.dead && Math.random() < 0.01 && enemy.velocity.y === 0) {  // 1% chance per frame to jump
        enemy.velocity.y = -15;  // Jump up
        enemy.switchSprites('jump');
    }
}

// JavaScript to send POST request when game is completed
function markGameAsCompleted(wrapId) {
    if (!wrapId) {
        console.error("wrapId is undefined");
        return;
    }

    console.log("Attempting to mark game as completed with wrap ID:", wrapId);

    fetch(`/spotify/complete-game/${wrapId}/`, {  // Adjust if there's a namespace like `spotify`
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()  // Make sure to include CSRF token for Django
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            console.log(data.message); // Log success message
        } else if (data.error) {
            console.error("Error:", data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}













function determineWinner({ player, enemy, timerId }) {
    clearTimeout(timerId); // Stop the timer
    const displayText = document.querySelector('#displayText');
    displayText.style.display = 'flex';

    // Helper function to force death animation
    function forceDeathAnimation(character) {
        character.dead = true; // Mark as dead
        character.switchSprites('death'); // Trigger death sprite

        // Ensure death animation plays fully
        const deathInterval = setInterval(() => {
            if (character.framesCurrent < character.sprites.death.framesMax - 1) {
                character.framesCurrent++; // Advance the frame
            } else {
                clearInterval(deathInterval); // Stop when animation completes
            }
        }, 100); // Adjust for smooth animation based on frame rate
    }

    if (player.health === enemy.health) {
        displayText.innerHTML = 'TIE';

        player.health = 0;
        enemy.health = 0;

        gsap.to('#playerHealth', { width: `${player.health}%` });
        gsap.to('#enemyHealth', { width: `${enemy.health}%` });

        forceDeathAnimation(player);
        forceDeathAnimation(enemy);
    } else if (player.health < enemy.health) {
        displayText.innerHTML = 'LOSER';

        player.health = 0;
        gsap.to('#playerHealth', { width: `${player.health}%` });

        forceDeathAnimation(player);
    } else if (enemy.health < player.health) {
        displayText.innerHTML = 'WINNER';

        enemy.health = 0;
        gsap.to('#enemyHealth', { width: `${enemy.health}%` });

        forceDeathAnimation(enemy);

        // Mark the game as completed if player wins
        console.log('Player won, marking game as completed...');
        markGameAsCompleted(wrapId);
    }
}




// CSRF Token Helper Function
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

let timer = 60;
let timerId
function decreaseTimer() {
    if (timer > 0) {
        timerId = setTimeout(decreaseTimer, 1000)
        timer--
        document.querySelector('#timer').innerHTML = timer
    }

    if (timer == 0) {
        determineWinner({player, enemy, timerId})
    }
}
decreaseTimer()

const enableQuestionPrompt = true; // Set to `false` to disable questions and deal direct damage


function promptQuestion() {
    if (!wrapData) {
        console.error("wrapData is undefined or null.");
        return;
    }

    console.log("wrapData:", wrapData); // Debugging

    const questionTypes = ["top_track", "top_genre", "top_artist"];
    const selectedQuestionType = questionTypes[Math.floor(Math.random() * questionTypes.length)];

    let question = "";
    let correctAnswer = "";
    let options = [];

    if (selectedQuestionType === "top_track" && wrapData.top_tracks && wrapData.top_tracks.length > 0) {
        question = "What is your top track?";
        correctAnswer = wrapData.top_tracks[0].name;
        options = wrapData.top_tracks.map(track => track.name);
    } else if (selectedQuestionType === "top_genre" && wrapData.top_genres && wrapData.top_genres.length > 0) {
        question = "What is your top genre?";
        correctAnswer = wrapData.top_genres[0][0];
        options = wrapData.top_genres.map(genre => genre[0]);
    } else if (selectedQuestionType === "top_artist" && wrapData.top_artist) {
        question = "Who is your top artist?";
        correctAnswer = wrapData.top_artist.name; // Correctly extract name

        // Safely generate options
        options = wrapData.top_artists 
            ? wrapData.top_artists.map(artist => artist.name) 
            : [wrapData.top_artist.name];
    } else {
        console.error("Insufficient data for generating a question.");
        return;
    }

    console.log("Selected Question Type:", selectedQuestionType);
    console.log("Question:", question);
    console.log("Correct Answer:", correctAnswer);
    console.log("Options:", options);

    showQuestionModal(question, options, correctAnswer);
}


function showQuestionModal(question, options, correctAnswer) {
    const questionModal = document.getElementById('questionModal');
    const questionText = document.getElementById('questionText');
    const optionsList = document.getElementById('optionsList');

    // Pause the game
    cancelAnimationFrame(animationId);

    // Set question text
    questionText.textContent = question;

    // Shuffle options and map correct answer
    const shuffledOptions = options.map((option, index) => ({
        text: option,
        isCorrect: option === correctAnswer // Mark the correct answer
    })).sort(() => Math.random() - 0.5); // Shuffle the array

    // Clear previous options and add new ones
    optionsList.innerHTML = '';
    shuffledOptions.forEach((optionObj, index) => {
        const li = document.createElement('li');

        // Number span
        const numberSpan = document.createElement('span');
        numberSpan.classList.add('option-number');
        numberSpan.textContent = `${index + 1}:`;

        // Option text span
        const textSpan = document.createElement('span');
        textSpan.classList.add('option-text');
        textSpan.textContent = optionObj.text;

        // Append spans to list item
        li.appendChild(numberSpan);
        li.appendChild(textSpan);
        
        li.dataset.index = index;

        // Enable click to select
        li.onclick = () => {
            handleAnswerSelection(optionObj.isCorrect);
            closeQuestionModal(); // Close the modal after a selection
        };
        optionsList.appendChild(li);
    });

    // Show modal
    questionModal.style.display = 'flex';

    // Listen for number key press (1-5)
    document.addEventListener('keydown', handleKeyPress);

    function handleKeyPress(event) {
        const key = event.key;
        if (key >= '1' && key <= shuffledOptions.length.toString()) { // Check if key is within options range
            const selectedIndex = parseInt(key) - 1; // Convert key to index (1 = index 0, etc.)
            handleAnswerSelection(shuffledOptions[selectedIndex].isCorrect);
            closeQuestionModal(); // Close the modal after a selection
        }
    }

    // Function to handle answer selection
    function handleAnswerSelection(isCorrect) {
        if (isCorrect) {
            handleCorrectAnswer();
        } else {
            handleIncorrectAnswer();
        }
    }

    // Remove keydown listener and close modal
    function closeQuestionModal() {
        questionModal.style.display = 'none';
        document.removeEventListener('keydown', handleKeyPress);
        requestAnimationFrame(animate);  // Resume the game
    }
}

function selectOption(optionElement) {
    // Clear previous selection
    document.querySelectorAll('#optionsList li').forEach(li => li.classList.remove('selected'));
    optionElement.classList.add('selected');
}

function handleCorrectAnswer() {
    enemy.takeHit();
    gsap.to('#enemyHealth', { width: enemy.health + '%' });
    console.log("Correct answer! Attack successful.");

    // Check if enemy health reaches zero to end the game
    if (enemy.health <= 0) {
        determineWinner({ player, enemy, timerId });
    }
}

function handleIncorrectAnswer() {
    console.log("Incorrect answer! Attack failed.");
    displayTemporaryMessage("Incorrect answer!", 2000);
}

function closeQuestionModal() {
    document.getElementById('questionModal').style.display = 'none';
    requestAnimationFrame(animate);  // Resume the game
}

function displayTemporaryMessage(message, duration) {
    const displayText = document.querySelector('#displayText');
    displayText.innerHTML = message;
    displayText.style.display = 'flex';
    setTimeout(() => displayText.style.display = 'none', duration);
}

// Helper function to generate options around the correct value
function generateOptions(correctValue) {
    const options = [
        (correctValue + 0.1).toFixed(2),
        (correctValue - 0.1).toFixed(2),
        (correctValue + 0.2).toFixed(2),
        (correctValue - 0.2).toFixed(2),
        correctValue.toFixed(2)
    ];
    return options;
}

let animationId;

function animate() {
    animationId = window.requestAnimationFrame(animate);
    c.fillStyle = 'black';
    c.fillRect(0, 0, canvas.width, canvas.height);
    background.update();
    player.update();
    enemy.update();

    // Player movement
    player.velocity.x = 0;
    if (keys.a.pressed && player.lastKey === 'a') {
        player.velocity.x = -5;
        player.switchSprites('run');
    } else if (keys.d.pressed && player.lastKey === 'd') {
        player.velocity.x = 5;
        player.switchSprites('run');
    } else {
        player.switchSprites('idle');
    }

    // Player jumping & falling
    if (player.velocity.y < 0) {
        player.switchSprites('jump');
    } else if (player.velocity.y > 0) {
        player.switchSprites('fall');
    }

    // Enemy movement
    // enemy.velocity.x = 0;
    // if (keys.ArrowLeft.pressed && enemy.lastKey === 'ArrowLeft') {
    //     enemy.velocity.x = -5;
    //     enemy.switchSprites('run');
    // } else if (keys.ArrowRight.pressed && enemy.lastKey === 'ArrowRight') {
    //     enemy.velocity.x = 5;
    //     enemy.switchSprites('run');
    // } else {
    //     enemy.switchSprites('idle');
    // }

    // ai enemy
    enemyAI();

    // Enemy jumping & falling
    if (enemy.velocity.y < 0) {
        enemy.switchSprites('jump');
    } else if (enemy.velocity.y > 0) {
        enemy.switchSprites('fall');
    }

    // Detect collision for player’s attack and apply damage to the enemy
    // if (
    //     player.isAttacking &&
    //     rectangularCollision({ rectangle1: player, rectangle2: enemy })
    // ) {
    //     player.isAttacking = false; // Reset attacking state
    //     enemy.takeHit(); // Apply damage to enemy
    //     enemy.health -= 20; // Decrease enemy health
    //     document.querySelector('#enemyHealth').style.width = enemy.health + '%';

    //     // Check if enemy health reaches zero to end the game
    //     if (enemy.health <= 0) {
    //         determineWinner({ player, enemy, timerId });
    //     }
    // }

    if (
        player.isAttacking &&
        rectangularCollision({ rectangle1: player, rectangle2: enemy })
    ) {
        player.isAttacking = false; // Reset attacking state
    
        // Check the flag before prompting the question or dealing damage
        if (enableQuestionPrompt) {
            // Prompt the player with a question if enabled
            promptQuestion();
        } else {
            // Directly deal damage without prompting if questions are disabled
            enemy.takeHit();
            gsap.to('#enemyHealth', {
                width: enemy.health + '%'
            });
    
            console.log("Direct damage dealt to enemy!");
    
            // Check if enemy health reaches zero to end the game
            if (enemy.health <= 0) {
                determineWinner({ player, enemy, timerId });
            }
        }
    }    

    // Detect collision for enemy’s attack and apply damage to the player
    if (
        enemy.isAttacking &&
        rectangularCollision({ rectangle1: enemy, rectangle2: player })
    ) {
        enemy.isAttacking = false; // Reset attacking state
        player.takeHit(); // Apply damage to player
        gsap.to('#playerHealth', {
            width: player.health + '%'
        })

        // Check if player health reaches zero to end the game
        if (player.health <= 0) {
            determineWinner({ player, enemy, timerId });
        }
    }
}

animate()

function restartGame() {
    location.reload(); // Reloads the page to restart the game
}

// EVENT LISTENER

window.addEventListener('keydown', (event) => {
    if (!player.dead) {
        switch (event.key) {
            case 'd':
                keys.d.pressed = true
                player.lastKey = 'd'
                break
            case 'a':
                keys.a.pressed = true
                player.lastKey = 'a'
                break
            case 'w':
                player.velocity.y = -10
                break
            case ' ':
                player.attack()
                break
        }
    }
    
// ememy movement
    // if (!enemy.dead) {
    //     switch(event.key) {
    //         case 'ArrowRight':
    //             keys.ArrowRight.pressed = true
    //             enemy.lastKey = 'ArrowRight'
    //             break
    //         case 'ArrowLeft':
    //             keys.ArrowLeft.pressed = true
    //             enemy.lastKey = 'ArrowLeft'
    //             break
    //         case 'ArrowUp':
    //             enemy.velocity.y = -10
    //             break
    //         case 'ArrowDown':
    //             enemy.attack()
    //             break
    //     }
    // }
})

window.addEventListener('keyup', (event) => {
    switch (event.key) {
        case 'd':
            keys.d.pressed = false
            break
        case 'a':
            keys.a.pressed = false
            break
    }

// enemy movement
    // switch (event.key) {
    //     case 'ArrowRight':
    //         keys.ArrowRight.pressed = false
    //         break
    //     case 'ArrowLeft':
    //         keys.ArrowLeft.pressed = false
    //         break
    // }
})

// Helper function to handle both mouse and touch events
function addGamepadListeners(buttonId, onPress, onRelease) {
    const button = document.getElementById(buttonId);

    // Press event (mousedown + touchstart)
    button.addEventListener('mousedown', onPress);
    button.addEventListener('touchstart', (event) => {
        event.preventDefault(); // Prevent default touch behavior
        onPress(event);
    });

    // Release event (mouseup + touchend)
    button.addEventListener('mouseup', onRelease);
    button.addEventListener('touchend', (event) => {
        event.preventDefault(); // Prevent default touch behavior
        onRelease(event);
    });
}

// Add gamepad functionality
addGamepadListeners('left', () => {
    keys.a.pressed = true;
    player.lastKey = 'a'; // Move left
}, () => {
    keys.a.pressed = false;
});

addGamepadListeners('right', () => {
    keys.d.pressed = true;
    player.lastKey = 'd'; // Move right
}, () => {
    keys.d.pressed = false;
});

addGamepadListeners('up', () => {
    if (!player.dead) player.velocity.y = -10; // Jump
}, () => {}); // No action on release

addGamepadListeners('down', () => {
    if (!player.dead) player.attack(); // Attack
}, () => {}); // No action on release
