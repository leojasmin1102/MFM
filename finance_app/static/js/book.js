import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { TweenRunner } from '/static/js/animation.js';

function createLeatherTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, '#7d4d2c');
  gradient.addColorStop(1, '#4e2f1a');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < 17000; i += 1) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    const shade = 60 + Math.floor(Math.random() * 110);
    ctx.fillStyle = `rgba(${shade}, ${Math.floor(shade * 0.62)}, ${Math.floor(shade * 0.4)}, 0.08)`;
    ctx.fillRect(x, y, 2, 2);
  }

  ctx.strokeStyle = 'rgba(30, 16, 8, 0.32)';
  ctx.lineWidth = 18;
  ctx.strokeRect(38, 38, canvas.width - 76, canvas.height - 76);

  const tex = new THREE.CanvasTexture(canvas);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(2, 2);
  tex.needsUpdate = true;
  return tex;
}

function createLeatherRoughnessTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  const imageData = ctx.createImageData(canvas.width, canvas.height);
  for (let i = 0; i < imageData.data.length; i += 4) {
    const value = 140 + Math.floor(Math.random() * 100);
    imageData.data[i] = value;
    imageData.data[i + 1] = value;
    imageData.data[i + 2] = value;
    imageData.data[i + 3] = 255;
  }
  ctx.putImageData(imageData, 0, 0);

  const tex = new THREE.CanvasTexture(canvas);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(4, 4);
  tex.needsUpdate = true;
  return tex;
}

function createPaperTexture(record) {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#f8f2df';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < 12000; i += 1) {
    const alpha = Math.random() * 0.06;
    const shade = 190 + Math.floor(Math.random() * 35);
    ctx.fillStyle = `rgba(${shade}, ${shade}, ${shade - 5}, ${alpha})`;
    ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 1.8, 1.8);
  }

  ctx.strokeStyle = 'rgba(102, 116, 156, 0.25)';
  ctx.lineWidth = 2;
  for (let y = 190; y < canvas.height - 100; y += 90) {
    ctx.beginPath();
    ctx.moveTo(110, y);
    ctx.lineTo(canvas.width - 110, y);
    ctx.stroke();
  }

  ctx.strokeStyle = 'rgba(197, 96, 91, 0.38)';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(172, 85);
  ctx.lineTo(172, canvas.height - 85);
  ctx.stroke();

  ctx.fillStyle = '#3b2f2c';
  ctx.font = '600 50px "Segoe UI", sans-serif';
  ctx.fillText(`Date: ${record.date}`, 220, 190);
  ctx.fillText(`Amount: ${record.amount}`, 220, 300);

  ctx.font = '500 44px "Segoe UI", sans-serif';
  ctx.fillText('Description:', 220, 410);

  wrapText(ctx, record.description, 220, 495, 640, 58);

  const tex = new THREE.CanvasTexture(canvas);
  tex.anisotropy = 8;
  tex.needsUpdate = true;
  return tex;
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(' ');
  let line = '';
  let lineNum = 0;

  words.forEach((word) => {
    const testLine = `${line}${word} `;
    if (ctx.measureText(testLine).width > maxWidth && line.length > 0) {
      ctx.fillText(line.trim(), x, y + lineNum * lineHeight);
      line = `${word} `;
      lineNum += 1;
      return;
    }
    line = testLine;
  });

  if (line.trim()) {
    ctx.fillText(line.trim(), x, y + lineNum * lineHeight);
  }
}

export class Notebook {
  constructor() {
    this.group = new THREE.Group();
    this.pageWidth = 3.4;
    this.pageHeight = 4.8;
    this.pageDepth = 0.01;
    this.pages = [];
    this.currentIndex = 0;
    this.tweenRunner = new TweenRunner();
    this.isFlipping = false;
    this._buildShell();
  }

  _buildShell() {
    const leatherMap = createLeatherTexture();
    const roughnessMap = createLeatherRoughnessTexture();
    const coverMaterial = new THREE.MeshStandardMaterial({
      map: leatherMap,
      roughnessMap,
      roughness: 0.9,
      metalness: 0.05,
    });

    const coverGeometry = new THREE.BoxGeometry(this.pageWidth + 0.24, this.pageHeight + 0.2, 0.16);

    this.backCover = new THREE.Mesh(coverGeometry, coverMaterial);
    this.backCover.position.z = -0.16;
    this.backCover.receiveShadow = true;
    this.backCover.castShadow = true;
    this.group.add(this.backCover);

    this.frontCover = new THREE.Mesh(coverGeometry, coverMaterial.clone());
    this.frontCover.position.z = 0.16;
    this.frontCover.receiveShadow = true;
    this.frontCover.castShadow = true;
    this.group.add(this.frontCover);

    const spineGeometry = new THREE.BoxGeometry(0.2, this.pageHeight + 0.22, 0.4);
    const spine = new THREE.Mesh(spineGeometry, coverMaterial.clone());
    spine.position.x = -this.pageWidth / 2 - 0.12;
    spine.receiveShadow = true;
    spine.castShadow = true;
    this.group.add(spine);

    this.frontCoverPivot = new THREE.Group();
    this.frontCoverPivot.position.set(-this.pageWidth / 2 - 0.05, 0, 0.12);
    this.frontCover.position.x = this.pageWidth / 2 + 0.05;
    this.frontCoverPivot.add(this.frontCover);
    this.group.add(this.frontCoverPivot);
  }

  loadRecords(records) {
    this.pages.forEach(({ pivot, mesh }) => {
      mesh.material.map?.dispose();
      mesh.material.dispose();
      mesh.geometry.dispose();
      this.group.remove(pivot);
    });

    this.pages = [];
    this.currentIndex = 0;

    const safeRecords = records.length ? records : [{ date: 'N/A', amount: '0', description: 'No bookkeeping data yet.' }];

    safeRecords.forEach((record, index) => {
      const texture = createPaperTexture(record);
      const material = new THREE.MeshStandardMaterial({ map: texture, roughness: 0.86, metalness: 0.01, side: THREE.DoubleSide });
      const geometry = new THREE.BoxGeometry(this.pageWidth, this.pageHeight, this.pageDepth);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.castShadow = true;
      mesh.receiveShadow = true;

      const pivot = new THREE.Group();
      pivot.position.set(-this.pageWidth / 2, 0, 0.03 + index * 0.004);
      mesh.position.x = this.pageWidth / 2;
      pivot.add(mesh);

      this.group.add(pivot);
      this.pages.push({ pivot, mesh, flipped: false });
    });

    this._refreshLayering();
    this.frontCoverPivot.rotation.y = 0;
  }

  _refreshLayering() {
    this.pages.forEach((page, index) => {
      page.pivot.position.z = 0.03 + index * 0.004;
    });
  }

  flipForward() {
    if (this.isFlipping || this.currentIndex >= this.pages.length) {
      return;
    }

    if (this.currentIndex === this.pages.length - 1) {
      this._flipFrontCoverOpen();
    }

    const page = this.pages[this.currentIndex];
    this.isFlipping = true;

    const startRotation = page.pivot.rotation.y;
    const targetRotation = -Math.PI;

    this.tweenRunner.tween({
      duration: 700,
      onUpdate: (progress) => {
        page.pivot.rotation.y = startRotation + (targetRotation - startRotation) * progress;
      },
      onComplete: () => {
        page.flipped = true;
        this.currentIndex += 1;
        this.isFlipping = false;
      },
    });
  }

  flipBackward() {
    if (this.isFlipping || this.currentIndex <= 0) {
      return;
    }

    const page = this.pages[this.currentIndex - 1];
    this.isFlipping = true;

    const startRotation = page.pivot.rotation.y;
    const targetRotation = 0;

    this.tweenRunner.tween({
      duration: 700,
      onUpdate: (progress) => {
        page.pivot.rotation.y = startRotation + (targetRotation - startRotation) * progress;
      },
      onComplete: () => {
        page.flipped = false;
        this.currentIndex -= 1;
        this.isFlipping = false;
      },
    });

    if (this.currentIndex - 1 === 0) {
      this._closeFrontCover();
    }
  }

  _flipFrontCoverOpen() {
    this.tweenRunner.tween({
      duration: 620,
      onUpdate: (progress) => {
        this.frontCoverPivot.rotation.y = -Math.PI * progress;
      },
    });
  }

  _closeFrontCover() {
    const start = this.frontCoverPivot.rotation.y;
    this.tweenRunner.tween({
      duration: 520,
      onUpdate: (progress) => {
        this.frontCoverPivot.rotation.y = start + (0 - start) * progress;
      },
    });
  }
}