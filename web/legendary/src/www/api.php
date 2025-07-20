<?php

require_once 'config.php';

$dbh = new PDO(APP_DB_HOST, APP_DB_USER, APP_DB_PASS);

//
// DB functions
//
function db_escape_col($value) {
	return '`' . str_replace('`', '``', $value) . '`';
}

function db_query_one($query, $params) {
	global $dbh;
	$stmt = $dbh->prepare($query);
	$stmt->execute($params);
	return $stmt->fetch(PDO::FETCH_ASSOC);
}

//
// API functions
//
function api_return_json($code, $json) {
	http_response_code($code);
	header('Content-Type: application/json');
	echo json_encode($json);
	die;
}

function api_sig_check($api) {
	return 
		isset($_SERVER['HTTP_X_SIGNATURE'])
		&& hash_hmac('sha256', $api, APP_SECRET_KEY) === $_SERVER['HTTP_X_SIGNATURE'];
}

function api_sig_gen($api) {
	return hash_hmac('sha256', $api, APP_SECRET_KEY);
}

function api_route_check($api, $route, $callable, $needs_signed) {
	$matches = null;
	
	if (!preg_match('~^' . $route . '$~', $api, $matches)) {
		return;
	}

	array_shift($matches); 
	
	if ($needs_signed && !api_sig_check($api)) {
		api_return_json(403, ['error' => 'signature missing or incorrect']);
	}
	
	call_user_func_array($callable, $matches);
	die;
}

//
// Defined routes
//
function route_health() {
	api_return_json(200, ['health' => 'OK']);
}

function route_animal_by_name($name) {
	route_animal_by_name_with_fields($name, 'name,size,description,imagedir');
}

function route_animal_by_name_with_fields($name, $fields) {
	$fieldstr = join(',', array_map('db_escape_col', explode(',', $fields)));
	$animal = db_query_one("SELECT $fieldstr FROM animals WHERE name = ?" , [$name]);
	if (empty($animal)) {
		api_return_json(404, ['error' => 'not found']);
	}
	if (isset($animal['imagedir'])) {
		$animal['imagedir'] = $animal['imagedir'] . '/' . array_values(array_diff(scandir($animal['imagedir']), ['.', '..']))[0];
	}
	api_return_json(200, $animal);
}

//
// Main API func
//
function do_api($api) {
	try {
		api_route_check($api, '/api/health', 'route_health', false);
		api_route_check($api, '/api/animal/([^/]+)', 'route_animal_by_name', true);
		api_route_check($api, '/api/animal/([^/]+)/fields/([^/]+)', 'route_animal_by_name_with_fields', true);
	} catch (Exception $e) {
		var_dump($e);
		api_return_json(500, ['error' => 'server error']);
	}
	api_return_json(404, ['error' => 'not found']);
}
