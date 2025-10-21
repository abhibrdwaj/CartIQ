export default function BrandingPanel() {
  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.logo}>🛒 CartIQ</h1>
        <p style={styles.tagline}>
          AI-powered meal planning for your household
        </p>

        <div style={styles.features}>
          <div style={styles.feature}>
            <span style={styles.icon}>✨</span>
            <div>
              <h3 style={styles.featureTitle}>Smart Meal Planning</h3>
              <p style={styles.featureText}>
                Generate personalized meal plans based on your preferences and pantry
              </p>
            </div>
          </div>

          <div style={styles.feature}>
            <span style={styles.icon}>📋</span>
            <div>
              <h3 style={styles.featureTitle}>Intelligent Shopping Lists</h3>
              <p style={styles.featureText}>
                Automatic shopping lists that know what you already have at home
              </p>
            </div>
          </div>

          <div style={styles.feature}>
            <span style={styles.icon}>💰</span>
            <div>
              <h3 style={styles.featureTitle}>Budget Friendly</h3>
              <p style={styles.featureText}>
                Stay within budget while maintaining healthy, delicious meals
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px 40px',
    minHeight: '100vh',
    color: 'white',
  },
  content: {
    maxWidth: '500px',
  },
  logo: {
    fontSize: '48px',
    fontWeight: '700',
    margin: '0 0 20px 0',
    letterSpacing: '-1px',
  },
  tagline: {
    fontSize: '24px',
    lineHeight: '1.4',
    margin: '0 0 60px 0',
    opacity: 0.95,
    fontWeight: '300',
  },
  features: {
    display: 'flex',
    flexDirection: 'column',
    gap: '30px',
  },
  feature: {
    display: 'flex',
    gap: '20px',
    alignItems: 'flex-start',
  },
  icon: {
    fontSize: '32px',
    flexShrink: 0,
  },
  featureTitle: {
    fontSize: '18px',
    fontWeight: '600',
    margin: '0 0 8px 0',
  },
  featureText: {
    fontSize: '15px',
    margin: 0,
    opacity: 0.9,
    lineHeight: '1.5',
  },
};
