<?php

// Uncomment for development
// error_reporting(E_ALL);
// ini_set('display_errors', 1);

// Since we start in the public folder (if installed correctly), reset working dir to here.
chdir(dirname(__FILE__));

set_include_path(get_include_path() . PATH_SEPARATOR . './lib');
spl_autoload_register(function ($class_name) {
    require_once($class_name . '.php');
});

$yaml = new Yaml();
$config = $yaml->load('../config.yml');

function checkUserForm()
{
    $errors = array();
    if (empty($_POST['name'])) {
        $errors[] = "Enter a username.";
    }
    if (empty($_POST['password'])) {
        $errors[] = "Enter a password.";
    }
    if (empty($_POST['password_confirm'])) {
        $errors[] = "Enter a confirmation password.";
    }
    if ($_POST['password'] != $_POST['password_confirm']) {
        $errors[] = "Password and confirmation password must match.";
    }

    return $errors;
}

function insertUser($db, $name, $password)
{
    $db->prepare('INSERT INTO users (name, password_hash, admin) VALUES (:name, :password_hash, 1);')
        ->execute(array(
            ':name' => $name,
            ':password_hash' => password_hash($password, PASSWORD_DEFAULT),
        ));
}

function createTables($db)
{
    $db->prepare('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, password_hash TEXT, admin INTEGER);')
        ->execute();
    $db->prepare('CREATE TABLE jobs
        (id INTEGER PRIMARY KEY, version TEXT, tag_name TEXT, config TEXT, pid INTEGER,
        started DATETIME, completed DATETIME, status TEXT, output TEXT);')->execute();
}


// Establish our primary DB connection
define('DBNAME', 'data/fsobuild.db');
if (file_exists(DBNAME)) {
    $db = new PDO('sqlite:'.DBNAME);
} else {
    if (!empty($_POST['add_user'])) {
        $errors = checkUserForm();

        if (empty($errors)) {
            // Create and populate new database.
            $db = new PDO('sqlite:'.DBNAME);
            createTables($db);
            insertUser($db, $_POST['name'], $_POST['password']);

            header('Location: '.$_SERVER['PHP_SELF']);
            exit;
        }
    }

    // Include the setup template since we have no DB.
    include('templates/setup.php');
    exit;
}

session_start();
// Do authentication checks, send to auth login, etc.
if (!empty($_GET['logout'])) {
    unset($_SESSION['loggedin']);
}

if (empty($_SESSION['loggedin']) && !(isset($_GET['invite']) && $_GET['invite'] === 'scp-devs')) {
    if (!empty($_POST['login'])) {
        $sth = $db->prepare("SELECT id, password_hash FROM users WHERE name=:name");
        $sth->execute(array(
                ':name' => $_POST['name'],
            ));
        $result = $sth->fetch(PDO::FETCH_ASSOC);
        if (!empty($result['id']) && password_verify($_POST['password'], $result['password_hash'])) {
            $_SESSION['loggedin'] = true;
            header('Location: '.$_SERVER['PHP_SELF']);
            exit;
        }
    }

    // Show log in page and exit.
    include('templates/login.php');
    exit;
}
session_write_close();

if (!empty($_GET['adduser']) || !empty($_GET['invite'])) {
    if (!empty($_POST['add_user'])) {
        $errors = checkUserForm();

        if (empty($errors)) {
            insertUser($db, $_POST['name'], $_POST['password']);

            header('Location: '.$_SERVER['PHP_SELF']);
            exit;
        }
    }

    // Include the setup template since we have no DB.
    include('templates/setup.php');
    exit;
}

// Handle output requests
if (!empty($_GET['buildid'])) {
    $sth = $db->prepare("SELECT output FROM jobs WHERE id=:id");
    $sth->execute(array(
            ':id' => $_GET['buildid'],
        ));
    $result = $sth->fetch(PDO::FETCH_ASSOC);
    header('Content-Type: text/plain');
    print $result['output'];
    exit;
}

// Handle ajax build status update requests
if (!empty($_GET['statuscheck'])) {
    header('Content-Type: application/json');
    echo json_encode(BuildTable::getBuilds($db));
    exit;
}

// Handle job runs
if (!empty($_POST['version'])) {
    $db->prepare("INSERT INTO jobs (version, tag_name, config, pid, started, status)
                VALUES (:version, :tag_name, '', ".getmypid().", CURRENT_TIMESTAMP, 'running');")
        ->execute(array(
            ':version' => $_POST['version'],
            ':tag_name' => $_POST['tag_name'],
        ));
    $args = escapeshellcmd($_POST['version']);
    if (!empty($_POST['tag_name'])) {
        $args .= " ".escapeshellcmd($_POST['tag_name']);
    }
    $output = file_get_contents($config['webui']['host'].'/trigger/release?api_key='.$config['webui']['key'].'&version=' . urlencode($_POST['version']) . '&tag_name=' . urlencode($_POST['tag_name']));
    $db->prepare("UPDATE jobs SET completed = CURRENT_TIMESTAMP, status = 'complete', output = :output
                WHERE pid=".getmypid()." AND status='running';")
        ->execute(array(
            ':output' => $output,
        ));
}

// Handle default page
$builds = BuildTable::getBuilds($db);
$fields = BuildTable::$fields;

include('templates/main.php');
