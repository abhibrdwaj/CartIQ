import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    const { error } = await signOut();
    if (!error) {
      navigate('/login');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>Dashboard</h1>
          <button onClick={handleLogout} style={styles.logoutButton}>
            Logout
          </button>
        </div>

        <div style={styles.content}>
          <div style={styles.welcomeBox}>
            <h2 style={styles.welcomeTitle}>Welcome to CartIQ!</h2>
            <p style={styles.userInfo}>
              Logged in as: <strong>{user?.email}</strong>
            </p>
            {user?.user_metadata?.first_name && (
              <p style={styles.userInfo}>
                Name: <strong>{user.user_metadata.first_name} {user.user_metadata.last_name}</strong>
              </p>
            )}
          </div>

          <div style={styles.infoBox}>
            <h3 style={styles.infoTitle}>Your meal planning assistant is ready!</h3>
            <p style={styles.infoText}>
              CartIQ will help you plan meals, manage your pantry, and generate smart shopping lists.
            </p>
            <p style={styles.infoText}>
              Coming soon: Meal planning features, pantry management, and AI-powered shopping lists.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  card: {
    backgroundColor: 'white',
    padding: '40px 60px',
    minHeight: '100vh',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '40px',
    paddingBottom: '24px',
    borderBottom: '2px solid #f0f0f0',
  },
  title: {
    margin: 0,
    fontSize: '36px',
    color: '#333',
    fontWeight: '700',
  },
  logoutButton: {
    padding: '12px 24px',
    fontSize: '15px',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#dc3545',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    maxWidth: '1200px',
  },
  welcomeBox: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '32px',
    borderRadius: '12px',
    color: 'white',
  },
  welcomeTitle: {
    margin: '0 0 20px 0',
    fontSize: '28px',
    fontWeight: '700',
  },
  userInfo: {
    margin: '10px 0',
    fontSize: '17px',
    opacity: 0.95,
  },
  infoBox: {
    backgroundColor: '#ffffff',
    padding: '32px',
    borderRadius: '12px',
    border: '2px solid #e0e0e0',
  },
  infoTitle: {
    margin: '0 0 16px 0',
    fontSize: '22px',
    color: '#333',
    fontWeight: '600',
  },
  infoText: {
    margin: '12px 0',
    fontSize: '16px',
    color: '#666',
    lineHeight: '1.7',
  },
};
