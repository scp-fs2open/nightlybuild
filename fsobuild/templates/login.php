<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>FSO Build Runner - Login</title>
    <meta name="description" content="The SCP Build Runner for FSO">
    <meta name="author" content="Cliff 'chief1983' Gordon">
</head>
<body>
    <h2>Login</h2>
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
                <td colspan="2"><input type="submit" name="login" id="login" value="Login" /></td>
            </tr>
        </table>
    </form>
</body>
</html>
