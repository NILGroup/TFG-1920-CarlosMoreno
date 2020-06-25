<!DOCTYPE html>
<html lang="es">
	<head>
		<meta charset="utf-8">
	</head>
	<body>
	<?php
		$ident = $_GET['id'];
		$command = escapeshellcmd("muestracorreo.py $ident");
		//output variable is a dictionary with the email information
		$output = json_decode(shell_exec($command), true);
		echo '<h1>' . $output['Subject'] . '</h1>';
		echo '<p>From: ' . $output['From'] . '</p>';
		echo '<p>' . $output['Text'] . '</p>';
	?>
	</body>
</html>