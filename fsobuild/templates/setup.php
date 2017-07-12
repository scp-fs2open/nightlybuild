<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>FSO Build Runner - Add User</title>
    <meta name="description" content="The SCP Build Runner for FSO">
    <meta name="author" content="Cliff 'chief1983' Gordon">
</head>
<body>
    <h2>Add User</h2>
    <?php if (!empty($errors)): ?>
    <?=implode("<br />\n", $errors)?>
    <?php endif; ?>
    <form action="<?=$_SERVER['PHP_SELF'].'?'.$_SERVER['QUERY_STRING']?>" method="POST">
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
                <td colspan="2"><input type="submit" name="add_user" id="add_user" value="Add User" /></td>
            </tr>
        </table>
    </form>
</body>
</html>
