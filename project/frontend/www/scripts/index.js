import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
    50, 
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setClearColor("#16161d")
document.body.appendChild( renderer.domElement );

camera.translateX(0);
camera.translateZ(61);
camera.translateY(-57);


// camera.translateX(-24.37);
// camera.translateZ(27.19);
// camera.translateY(42.75);

// camera.translateX(-121.85);
// camera.translateZ(135.95);
// camera.translateY(-213.75);

camera.rotateX(Math.PI / 4); // 60 deg

// Axis Display
const axesHelper = new THREE.AxesHelper();
axesHelper.translateX(0)
axesHelper.translateY(0)
axesHelper.translateZ(1.5)
scene.add(axesHelper);

// Table
const table1Material = new THREE.LineBasicMaterial({ color: 0xf2392c }); // 0x03b6fc
const tableGeometry = new THREE.BoxGeometry(67, 42, 0.5);
const table1 = new THREE.Mesh(tableGeometry, table1Material);
table1.position.y = 0;
table1.position.z = 1;

// Table Edges
const tableEdgeGeometry = new THREE.EdgesGeometry(table1.geometry);
const tableEdgeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
const tableWireframe = new THREE.LineSegments(tableEdgeGeometry, tableEdgeMaterial);

table1.add(tableWireframe)
scene.add(table1)

const geometry = new THREE.SphereGeometry( 2, 32, 16 );
const material = new THREE.MeshBasicMaterial( { color: 0xffffff } );
const sphere = new THREE.Mesh( geometry, material );
sphere.translateZ(2.5);

scene.add(sphere);

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

let polling = setInterval(() => {
    try {
        $.get("http://10.115.9.91:5005/position", function(data) {
            const position_incoming = JSON.parse(data)
            position.x = position_incoming.position[0] * 1
            position.y = position_incoming.position[1] * 1
            
            if(!position_incoming.in_field) {
                table1.material.color.setHex(0x4c8f46)
            }
            else {
                table1.material.color.setHex(0xf2392c)
            }
        })
    } catch (error) {
        table1.material.color.setHex(0xe8e805)
    }
}, 3000)


function animate() {
	requestAnimationFrame( animate );

    const v = new THREE.Vector3(position.x, position.y, position.z + 2.5)
    sphere.position.lerp(v, 0.05)

	renderer.render( scene, camera );
}
animate();
