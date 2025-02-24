document.addEventListener('DOMContentLoaded', function () {
    const pixelGrid = document.getElementById('pixel-grid');
    const colorPicker = document.getElementById('color');
    const clearButton = document.getElementById('clear-button');
    const zoomInButton = document.getElementById('zoom-in');
    const zoomOutButton = document.getElementById('zoom-out');
    const saveButton = document.getElementById('save-button');
    const zoomWarning = document.getElementById('zoom-warning');
    const toggleButton = document.getElementById('toggle-dark-mode');

    let gridSize = 16; // Initial grid size (16x16)
    const maxGridSize = 32; // Maximum grid size limit (32x32)
    const minGridSize = 8;  // Minimum grid size limit (8x8)

    // Function to create the grid
    function createGrid() {
        pixelGrid.innerHTML = ''; // Clear previous grid
        pixelGrid.style.gridTemplateColumns = `repeat(${gridSize}, 20px)`;
        pixelGrid.style.gridTemplateRows = `repeat(${gridSize}, 20px)`;

        for (let i = 0; i < gridSize * gridSize; i++) {
            const pixel = document.createElement('div');
            pixel.classList.add('pixel');
            pixel.addEventListener('click', function () {
                pixel.style.backgroundColor = colorPicker.value;
            });
            pixelGrid.appendChild(pixel);
        }
    }

    // Function to clear the grid
    clearButton.addEventListener('click', function () {
        const pixels = pixelGrid.getElementsByClassName('pixel');
        Array.from(pixels).forEach(pixel => {
            pixel.style.backgroundColor = '#fff';
        });
    });

    // Zoom In (Increase grid size by 1 row and column)
    zoomInButton.addEventListener('click', function () {
        if (gridSize < maxGridSize) {
            gridSize++; // Increase the grid size
            createGrid(); // Re-create grid with the new size
            zoomWarning.classList.remove('hidden'); // Show the warning when zooming in
        }
    });

    // Zoom Out (Decrease grid size by 1 row and column)
    zoomOutButton.addEventListener('click', function () {
        if (gridSize > minGridSize) {
            gridSize--; // Decrease the grid size
            createGrid(); // Re-create grid with the new size
            zoomWarning.classList.add('hidden'); // Hide the warning when zooming out
        }
    });

    // Save Art
    saveButton.addEventListener('click', function () {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const pixels = pixelGrid.getElementsByClassName('pixel');
        const pixelArray = Array.from(pixels);

        canvas.width = gridSize * 20; // Adjust the canvas width
        canvas.height = gridSize * 20; // Adjust the canvas height

        pixelArray.forEach((pixel, index) => {
            const x = (index % gridSize) * 20;
            const y = Math.floor(index / gridSize) * 20;
            const color = pixel.style.backgroundColor || '#fff';
            ctx.fillStyle = color;
            ctx.fillRect(x, y, 20, 20);
        });

        const dataURL = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = dataURL;
        a.download = 'pixel-art.png';
        a.click(); // Trigger download
    });

    toggleButton.addEventListener('click', function () {
        console.log('Dark mode toggle clicked!');
        document.documentElement.classList.toggle('dark');
    });    
    createGrid(); // Initial grid creation
});

/*
Example usage in HTML with TailwindCSS:

<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixel Art</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-white dark:bg-gray-800 text-black dark:text-white">
    <div id="pixel-grid" class="grid gap-1"></div>
    <input type="color" id="color" class="mt-2">
    <button id="clear-button" class="mt-2 p-2 bg-blue-500 text-white">Clear</button>
    <button id="zoom-in" class="mt-2 p-2 bg-green-500 text-white">Zoom In</button>
    <button id="zoom-out" class="mt-2 p-2 bg-red-500 text-white">Zoom Out</button>
    <button id="save-button" class="mt-2 p-2 bg-yellow-500 text-white">Save</button>
    <button id="toggle-dark-mode" class="mt-2 p-2 bg-gray-500 text-white">Toggle Dark Mode</button>
    <div id="zoom-warning" class="hidden text-red-500">Maximum zoom level reached!</div>
    <script src="static/js/script.js"></script>
</body>
</html>
*/