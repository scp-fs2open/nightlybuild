<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>FSO Build Runner - Setup</title>
    <meta name="description" content="The SCP Build Runner for FSO">
    <meta name="author" content="Cliff 'chief1983' Gordon">
</head>
<body>
    <h2>Setup</h2>
    <?=implode("<br />\n", $errors)?>
    <form action="<?=$_SERVER['PHP_SELF']?>" method="POST">
        <table>
            <tr>
                <td><label for="name">Name</label></td>
                <td><input type="text" id="name" name="name" /></td>
            </tr>
            <tr>
                <td><label for="password">Password</label></td>
                <td><input type="password" id="password" name="password" /></td>
            </tr>
            <tr>
                <td><label for="password">Repeat Password</label></td>
                <td><input type="password" id="password_confirm" name="password_confirm" /></td>
            </tr>
            <tr>
                <td colspan="2"><input type="submit" name="setup" id="setup" value="Install" /></td>
            </tr>
        </table>
    </form>
</body>
</html>
