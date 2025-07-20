<?php

require_once 'api.php';

$api = urldecode(parse_url($_SERVER['PATH_INFO'])['path']);

if (str_starts_with($api, '/api/')) {
	do_api($api);	
	die;
}

?><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legendary</title>
    <link rel="stylesheet" href="/static/css/app.css">
    <script src="/static/js/app.js" defer></script>
</head>
<body>
    <!-- Footprint decorations -->
    <div class="footprint"></div>
    <div class="footprint"></div>
    <div class="footprint"></div>
    <div class="footprint"></div>
    <div class="footprint"></div>
    <div class="footprint"></div>

    <div class="container">
        <h1>legendary</h1>
        <p class="subtitle">
            click for information about the <a href="#" class="animal-link" data-animal="quokka">quokka</a>, 
            <a href="#" class="animal-link" data-animal="emu">emu</a>, or 
            <a href="#" class="animal-link" data-animal="kangaroo">kangaroo</a>
        </p>
    </div>

    <!-- Modal -->
    <div id="animalModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalBody">
                <div class="loading">Loading animal information...</div>
            </div>
        </div>
    </div>

    <script>
        const APP_SIGNATURES = {
            quokka: '<?= api_sig_gen('/api/animal/quokka'); ?>',
            emu: '<?= api_sig_gen('/api/animal/emu'); ?>',
            kangaroo: '<?= api_sig_gen('/api/animal/kangaroo'); ?>'
        }
    </script>
</body>
</html>