<!DOCTYPE html>
<html lang="es">
	<head>
		<meta charset="utf-8">
	</head>
	<body>
	<h1>Lista de correos electrónicos del usuario</h1>
	<?php
			$command = escapeshellcmd('listacorreos.py');
			//output variable is a dictionary with the emails
			$output = json_decode(shell_exec($command), true);
			echo '<table border="1">';
			echo '<tr> <td>From</td> <td>Subject</td> <td>Snippet</td> </tr>';
			for ($i = 0; $i < $output['length']; $i++){
				echo '<tr> <td> <a href="muestracorreo.php?id=' .$output[strval($i)]['Id'] . '">' . $output[strval($i)]['From'] . '</td> <td>' . $output[strval($i)]['Subject'] . '</td> <td>' . $output[strval($i)]['Snippet'] . '</a> </td> </tr>';
			}
			echo '</table>';
		?>
	</body>
</html> 