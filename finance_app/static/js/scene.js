
import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { Notebook } from '/static/js/book.js';

export class NotebookScene {
  constructor(container) {
    this.container = container;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color('#d5c2a5');

    this.camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    this.camera.position.set(0, 2.3, 6.5);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.enablePan = false;
    this.controls.minDistance = 4.6;
    this.controls.maxDistance = 9;
    this.controls.minPolarAngle = 0.7;
    this.controls.maxPolarAngle = 1.45;

    this.notebook = new Notebook();
    this.notebook.group.position.y = 0.08;
    this.notebook.group.rotation.x = -0.14;
    this.scene.add(this.notebook.group);

    this._buildLights();
    this._buildDesk();

    this.renderer.domElement.addEventListener('click', (event) => {
      const rect = this.renderer.domElement.getBoundingClientRect();
      const x = event.clientX - rect.left;
      if (x > rect.width * 0.54) {
        this.notebook.flipForward();
      } else {
        this.notebook.flipBackward();
      }
    });

    window.addEventListener('resize', () => this._onResize());
    this._animate();
  }

  _buildLights() {
    const ambient = new THREE.AmbientLight('#fff7e1', 0.7);
    this.scene.add(ambient);

    const directional = new THREE.DirectionalLight('#fff5dc', 1.05);
    directional.position.set(4.5, 6.5, 3.5);
    directional.castShadow = true;
    directional.shadow.mapSize.width = 2048;
    directional.shadow.mapSize.height = 2048;
    directional.shadow.camera.near = 0.5;
    directional.shadow.camera.far = 20;
    directional.shadow.camera.left = -6;
    directional.shadow.camera.right = 6;
    directional.shadow.camera.top = 6;
    directional.shadow.camera.bottom = -6;
    this.scene.add(directional);
  }

  _buildDesk() {
    const desk = new THREE.Mesh(
      new THREE.PlaneGeometry(18, 14),
      new THREE.MeshStandardMaterial({ color: '#9f7b5b', roughness: 0.9, metalness: 0.05 }),
    );
    desk.rotation.x = -Math.PI / 2;
    desk.position.y = -2.45;
    desk.receiveShadow = true;
    this.scene.add(desk);
  }

  setRecords(records) {
    this.notebook.loadRecords(records);
  }

  flipForward() {
    this.notebook.flipForward();
  }

  flipBackward() {
    this.notebook.flipBackward();
  }

  _onResize() {
    const { clientWidth, clientHeight } = this.container;
    this.camera.aspect = clientWidth / clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(clientWidth, clientHeight);
  }

  _animate() {
    requestAnimationFrame(() => this._animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
