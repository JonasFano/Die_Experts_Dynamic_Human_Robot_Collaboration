<?php

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Content-Type: application/json");
header("X-Robots-Tag: noindex, nofollow", true);

$data_file = './data/'.date('Y-m-d').'.json';
$latest_entries_count = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;

// Ensure the data file exists
if (!file_exists($data_file)) {
    file_put_contents($data_file, json_encode([]));
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Try to handle JSON input first
    $input = file_get_contents('php://input');
    $json_data = json_decode($input, true);
    
    // If JSON input is not valid, treat it as form-encoded data
    if (json_last_error() !== JSON_ERROR_NONE) {
        $json_data = $_POST; // Capture form data as an associative array
    }

    // Create an array to store the existing data
    $existing_data = [];

    // If the data file exists, load the existing data
    if (file_exists($data_file)) {
        $file_contents = file_get_contents($data_file);
        $existing_data = json_decode($file_contents, true);
        
        // If there's no valid array in the file, set existing_data to an empty array
        if (!is_array($existing_data)) {
            $existing_data = [];
        }
    }

    // Append the new data to the existing data
    $existing_data[] = $json_data;

    // Save the updated data back to the file in append mode
    file_put_contents($data_file, json_encode($existing_data, JSON_PRETTY_PRINT));

    // Respond with success message
    echo json_encode(["message" => "Data appended successfully!"]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($data_file)) {
        $file_contents = file_get_contents($data_file);
        $existing_data = json_decode($file_contents, true);

        if (is_array($existing_data)) {
            // Get the latest N entries
            $latest_data = array_slice($existing_data, -$latest_entries_count);
            echo json_encode($latest_data);
        } else {
            echo json_encode([]);
        }
    } else {
        echo json_encode([]);
    }
    exit;
}

?>
