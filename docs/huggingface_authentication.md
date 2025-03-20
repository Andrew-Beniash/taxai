# Setting Up Hugging Face Authentication

The Mistral-7B model requires authentication to download from Hugging Face. Here's how to set up access:

## 1. Get a Hugging Face Token

1. Create an account on [Hugging Face](https://huggingface.co/) if you don't have one
2. Go to your profile settings: https://huggingface.co/settings/tokens
3. Create a new token with read permissions
4. Copy the token value

## 2. Set Up Your Token (Choose One Method)

### Method A: Environment Variable (Recommended)

Add the token to your environment:

```bash
# Add to your shell startup file (.bashrc, .zshrc, etc.)
export HUGGINGFACE_TOKEN="your_token_here"

# Or for just the current session
export HUGGINGFACE_TOKEN="your_token_here"
```

Then restart your shell or run:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Method B: Using .env File

Add the token to your project's `.env` file:

```
HUGGINGFACE_TOKEN=your_token_here
```

### Method C: Hugging Face CLI (Alternative)

Install and log in with the Hugging Face CLI:

```bash
pip install huggingface_hub
huggingface-cli login
```

This will store your token in `~/.huggingface/token`.

## 3. Test Your Setup

After setting up your token, run the test script again:

```bash
./test_ai_processing.sh
```

If everything is set up correctly, you should be able to download and use the Mistral-7B model.

## Troubleshooting

If you still encounter authentication issues:

1. Verify you have the correct token with appropriate permissions
2. Check that the environment variable is properly set: `echo $HUGGINGFACE_TOKEN`
3. Make sure the token has access to the specific model you're trying to use
4. If you're using a corporate network, check for any proxy or firewall settings

## Note on Model Access

Some models on Hugging Face require accepting terms and conditions before use. If you're still having trouble after setting up authentication:

1. Visit the model page directly: [mistralai/Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1)
2. Check if there's a "Sign Model Use Agreement" button
3. Accept the terms if required
