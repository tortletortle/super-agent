"""游戏 Agent：游戏开发、Three.js 模板

能力：
1. Three.js 基础场景模板生成
2. 跑酷/超休闲游戏模板
3. HTML 游戏文件生成
"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class GameAgent(Agent):
    name = "game"
    description = "Three.js 游戏开发、3D 场景、HTML 游戏文件生成"

    def run(self, task: Task) -> TaskResult:
        content = task.content
        c = content.lower()

        if "three" in c or "3d" in c or "3d场景" in c:
            return self._three_template(content)
        if "跑酷" in c or "runner" in c or "超休闲" in c:
            return self._runner_template(content)
        if "html" in c or "页面" in c or "网页" in c:
            return self._html_template(content)

        return TaskResult(
            task_id=task.id, agent_name=self.name,
            output="GameAgent 可用模板:\n"
                   "  • Three.js 场景: 'Three.js 3D场景'\n"
                   "  • 跑酷游戏: '生成跑酷游戏'\n"
                   "  • HTML 游戏: 'HTML 游戏页面'\n"
                   "提示: 生成的代码需要保存到 .html 文件运行"
        )

    def _three_template(self, content: str) -> TaskResult:
        return TaskResult(
            task_id="", agent_name=self.name,
            output="""📦 Three.js 基础场景模板

```html
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Three.js 场景</title>
<style>body{margin:0;overflow:hidden}</style></head><body>
<script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js"}}</script>
<script type="module">
import * as THREE from 'three';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xede9fe); // 浅紫

const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(0, 5, 10);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 地面
const geo = new THREE.PlaneGeometry(10, 20);
const mat = new THREE.MeshLambertMaterial({color: 0xc4b5fd});
const ground = new THREE.Mesh(geo, mat);
ground.rotation.x = -Math.PI/2;
scene.add(ground);

// 灯光
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 10, 7);
scene.add(light);

// 方块
const box = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshLambertMaterial({color: 0x3b82f6})
);
box.position.y = 0.5;
scene.add(box);

function animate() {
  requestAnimationFrame(animate);
  box.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script></body></html>
```
保存为 scene.html 用浏览器打开"""
        )

    def _runner_template(self, content: str) -> TaskResult:
        return TaskResult(
            task_id="", agent_name=self.name,
            output="""🏃 跑酷游戏模板

```html
<!DOCTYPE html><html><head><meta charset="utf-8"><title>跑酷</title>
<style>body{margin:0;overflow:hidden;background:#ede9fe}</style></head><body>
<script type="text/javascript">
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// 简单 2D 跑酷
const player = {x: 100, y: 300, w: 30, h: 30, vy: 0, jumping: false};
const gravity = 0.6;
const groundY = 360;
const obstacles = [];
let score = 0;
let gameOver = false;

function jump() {
  if (!player.jumping) {
    player.vy = -10;
    player.jumping = true;
  }
}

function update() {
  if (gameOver) return;
  player.vy += gravity;
  player.y += player.vy;
  if (player.y >= groundY - player.h) {
    player.y = groundY - player.h;
    player.vy = 0;
    player.jumping = false;
  }
  // 障碍物
  if (Math.random() < 0.02) {
    obstacles.push({x: canvas.width, y: groundY - 30, w: 20, h: 30});
  }
  for (let i = obstacles.length - 1; i >= 0; i--) {
    obstacles[i].x -= 5;
    // 碰撞检测
    if (player.x < obstacles[i].x + obstacles[i].w &&
        player.x + player.w > obstacles[i].x &&
        player.y < obstacles[i].y + obstacles[i].h &&
        player.y + player.h > obstacles[i].y) {
      gameOver = true;
    }
    if (obstacles[i].x < -50) obstacles.splice(i, 1);
  }
  score++;
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  // 地面
  ctx.fillStyle = '#c4b5fd';
  ctx.fillRect(0, groundY, canvas.width, 10);
  // 玩家
  ctx.fillStyle = gameOver ? '#ef4444' : '#3b82f6';
  ctx.fillRect(player.x, player.y, player.w, player.h);
  // 障碍物
  ctx.fillStyle = '#f0f0f0';
  obstacles.forEach(o => ctx.fillRect(o.x, o.y, o.w, o.h));
  // 分数
  ctx.fillStyle = '#333';
  ctx.font = '20px Arial';
  ctx.fillText('分数: ' + Math.floor(score/10), 10, 30);
  if (gameOver) {
    ctx.fillStyle = 'red';
    ctx.font = '40px Arial';
    ctx.fillText('Game Over', canvas.width/2-100, canvas.height/2);
  }
}

document.addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); jump(); } });
canvas.addEventListener('click', jump);

function loop() { update(); draw(); requestAnimationFrame(loop); }
loop();
</script>
<canvas id="game"></canvas>
</body></html>
```
保存为 runner.html 用浏览器打开，空格/点击跳跃"""
        )

    def _html_template(self, content: str) -> TaskResult:
        return TaskResult(
            task_id="", agent_name=self.name,
            output="""📄 HTML 游戏页面模板

```html
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>游戏</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #ede9fe; display: flex; justify-content: center; align-items: center; height: 100vh; }
canvas { background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
</style></head><body>
<canvas id="gc"></canvas>
<script>
const canvas = document.getElementById('gc');
const ctx = canvas.getContext('2d');
canvas.width = 400;
canvas.height = 600;

// 在这里写你的游戏逻辑
function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#3b82f6';
  ctx.fillRect(180, 280, 40, 40);
  requestAnimationFrame(draw);
}
draw();
</script></body></html>
```
保存为 game.html 用浏览器打开"""
        )