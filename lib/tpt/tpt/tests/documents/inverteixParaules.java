package tests.documents; /**@file inverteixParaules.java
 * Exercici 3 Unitat 2 Taller de Java
 * Universitat Oberta de Catalunya
 * 
 * Feu un programa que donada una frase posi les paraules de la frase en ordre invers.
 * fent servir la entrada estandard
 */

/**
 * @author Oriol Aldea
 * @version 1.0
 * @date 16-02-2010
 */
import java.util.*;
public class inverteixParaules {
	/**
	 * @param args
	 */
	
	public static void main(String[] args) {
		System.out.println("Escriu la frase (Enter per a acabar): ");
		Scanner in = new Scanner(System.in);
		String aux = "";
		aux=in.nextLine();
		StringTokenizer frase = new StringTokenizer(aux);
		aux="";
		   while (frase.hasMoreTokens()) {
		         aux=frase.nextToken() + " " + aux;
		   }
		System.out.println("Frase invertida: " + aux);
	}
}
