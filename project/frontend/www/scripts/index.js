import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
    60, 
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setClearColor("#16161d")
document.body.appendChild( renderer.domElement );

camera.translateX(-6.5);
camera.translateZ(7.65);
camera.translateY(-11.4);
camera.rotateZ(-Math.PI / 6); // 30 deg
camera.rotateX(Math.PI / 3); // 60 deg

// Axis Display
const axesHelper = new THREE.AxesHelper();
axesHelper.translateX(5)
axesHelper.translateY(5)
axesHelper.translateZ(5)
scene.add(axesHelper);

// Table
const table1Material = new THREE.LineBasicMaterial({ color: 0x03b6fc });
const tableGeometry = new THREE.BoxGeometry(8, 12, 0.5);
const table1 = new THREE.Mesh(tableGeometry, table1Material);
table1.position.y = 0;
table1.position.z = 1;

// Table Edges
const tableEdgeGeometry = new THREE.EdgesGeometry(table1.geometry);
const tableEdgeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
const tableWireframe = new THREE.LineSegments(tableEdgeGeometry, tableEdgeMaterial);

table1.add(tableWireframe)
scene.add(table1)

const geometry = new THREE.SphereGeometry( 0.25, 32, 16 );
const material = new THREE.MeshBasicMaterial( { color: 0xffffff } );
const sphere = new THREE.Mesh( geometry, material );
sphere.translateZ(3);

scene.add(sphere);


// Application
// let count = 0
// const r = 2

let position = {
    x: 0,
    y: 0,
    z: 0,
}

window.addEventListener("resize", function(_) {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
    return;
})

const socket = new WebSocket("ws://localhost:8765");

socket.addEventListener("message", function(event) {
    const { data } = event;
    const pos = JSON.parse(data);
    const isDataCorrect = ["x", "y", "z"].every(coord => coord in pos);

    if (!isDataCorrect) {
        console.log("Incorrrect format for data")
        return;
    }

    position.x = pos.x;
    position.y = pos.y;
    position.z = pos.z;
    return;
})

function animate() {
	requestAnimationFrame( animate );

    // sphere.position.x = position.x;
    // sphere.position.y = position.y;
    // sphere.position.z = position.z + 3;

    const v = new THREE.Vector3(position.x, position.y, position.z + 2)
    sphere.position.lerp(v, 0.1)

	renderer.render( scene, camera );
}
animate();
