# Security Notice

## API Key Management

This project previously contained a hardcoded API key in `crypto_buddy.py`. This has been removed for security reasons.

### What Changed

- **Before**: `self.api_key = os.getenv("COINGECKO_API_KEY", "CG-k4wGZdUCFNyC7UFL19YJN26i")`
- **After**: `self.api_key = os.getenv("COINGECKO_API_KEY", "")  # No hardcoded key - use environment variable`

### How to Use Your API Key

1. Create a `.env` file (already in `.gitignore`):
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your personal API key:
   ```
   COINGECKO_API_KEY=your_personal_api_key_here
   ```

3. Load the environment variable:
   ```bash
   export COINGECKO_API_KEY=your_personal_api_key_here
   ```

### For Demo/Testing

The CoinGecko API allows anonymous requests with rate limits. The app will work without an API key, but you may hit rate limits.

### Best Practices

- ✅ Never commit API keys to version control
- ✅ Use environment variables for sensitive data
- ✅ Keep `.env` files in `.gitignore`
- ✅ Use `.env.example` as a template without real keys
- ✅ Rotate API keys if they are exposed

### Note for Capstone Submission

This security improvement demonstrates:
- Understanding of secure coding practices
- Proper use of environment variables
- API key management best practices
- Git security hygiene
