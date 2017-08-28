import java.util.Locale;

import javax.cim.CIMInstance;
import javax.cim.CIMObjectPath;
import javax.security.auth.Subject;
import javax.wbem.CloseableIterator;
import javax.wbem.WBEMException;
import javax.wbem.client.PasswordCredential;
import javax.wbem.client.UserPrincipal;
import javax.wbem.client.WBEMClient;
import javax.wbem.client.WBEMClientFactory;

/**
 * Ping - program that will connect to the server and enumerate
 * CIM_ComputerSystem. It will not display anything to the screen unless there
 * is an error.
 * 
 * <code> 
 * arg[0] = http://server[:port]/naamespace 
 * arg[1] = username 
 * arg[2] = password
 * </code>
 */
public class Ping {
	
	private static final int TIMEOUT = 20000;
	private String mUsername;
	private String mPassword;
	private CIMObjectPath mOP;
	

	public static void main(String args[]) throws WBEMException {
		Ping ping = new Ping(args);

		try {
			ping.run();
		} catch (Exception e) {
			System.err.println(e.getMessage());
			System.exit(1);
		}

	}

	public Ping(String args[]) {
		// Requires at least 3 command-line arguments.
		// If not all entered, prints command string.
		if (args.length < 3) {
			System.out.println("Ping <serverurl> <username> <password>");
			System.exit(1);
		}
		try {
			mOP = new CIMObjectPath(args[0]);
		} catch (Exception e) {
			System.err.println(e.getMessage());
			System.exit(1);
		}
		mUsername = args[1];
		mPassword = args[2];
	}

	public void run() throws WBEMException {
		ConnectionAttempt attempt = new ConnectionAttempt(mOP, mUsername,
				mPassword);
		attempt.start();
		try {
			attempt.join(TIMEOUT);
		} catch (InterruptedException e) {
		}

		if (attempt.isAlive())
			throw new RuntimeException("Timed out after " + TIMEOUT + "ms");

		attempt.rethrowFailure();
	}

	class ConnectionAttempt extends Thread {
		private static final String CCN_CIM_COMPUTERSYSTEM = "CIM_ComputerSystem";
		private CIMObjectPath mOP;
		private String username;
		private String password;
		private Throwable exception;

		public ConnectionAttempt(CIMObjectPath op, String username,
				String password) {
			mOP = op;
			this.username = username;
			this.password = password;
		}

		public void run() {
			try {
				UserPrincipal up = new UserPrincipal(username);
				// System.err.println("after UserPrincipal");
				PasswordCredential pc = new PasswordCredential(password);
				Subject subject = new Subject();
				subject.getPrincipals().add(up);
				subject.getPrivateCredentials().add(pc);
				// System.err.println("after PasswordCredential");
				WBEMClient cc = WBEMClientFactory.getClient("CIM-XML");
				Locale[] l = { Locale.ENGLISH };
				cc.initialize(mOP, subject, l);
				// System.err.println("after CIMClient");
				CIMObjectPath cop = new CIMObjectPath(mOP.getScheme(),
						mOP.getHost(), mOP.getPort(), mOP.getNamespace(),
						CCN_CIM_COMPUTERSYSTEM, null);
				CloseableIterator<CIMInstance> instIter = cc.enumerateInstances(cop, false, false, false, null);
				//while (instIter.hasNext()) {
				//	System.out.println(instIter.next());
				//}
				// System.err.println("after enumerateInstances");
				cc.close();
			} catch (WBEMException e) {
				exception = e;
			} catch (Throwable tr) {
				exception = tr;
			}
		}

		public void rethrowFailure() throws WBEMException {
			if (exception == null)
				return;

			else if (exception instanceof WBEMException)
				throw (WBEMException) exception;

			else if (exception instanceof RuntimeException)
				throw (RuntimeException) exception;

			else if (exception instanceof Error)
				throw (Error) exception;

			else
				// should never get here
				throw new RuntimeException("Unexpected Exception", exception);
		}
	}
}
