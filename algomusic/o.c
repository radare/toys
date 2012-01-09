/* http://lolcathost.org/b/Makefile */
#include <SDL.h>
#include <SDL_audio.h>

static Uint8 *audio_chunk;
static Uint32 audio_len;
static Uint8 *audio_pos;

static int t = 0;

static void generate (int i, Uint8 *buf, int len) {
	int n = 0;
	for (t=i; n<len; t++,n++)
	//	buf[t] = (t*(((t>>12)|(t>>8))&(63&(t>>4))));
		//buf[t] = (t>>7|t|t>>6)*10+4*(t&t>>13|t>>6);
		//buf[t] = b = ((b>>1)+(b>>4))+ t*(((t>>16)|(t>>6))&69&(t>>9));
		//buf[t] = (t|(t>>9|t>>7))*t&(t>>11|t>>9);
		//buf[t] = t*5 & (t>>7)|t*3&(t*4>>10);
#ifdef F
		buf[t] = F;
#else
		buf[t] = t*8 & (t>>4)*(t*8&(t*4>>10));
#endif
}

static void mixaudio(void *udata, Uint8 *stream, int len) {
	if (audio_len == 0)
		return;
	// Mix as much data as possible 
	len = (len > audio_len ? audio_len : len);
	//generate (t, audio_pos, len);

	SDL_MixAudio (stream, audio_pos, len, SDL_MIX_MAXVOLUME);
	t += len;
	audio_pos += len;
	audio_len -= len;
}

int main(int argc, char **argv) {
	int length = 409600;
	SDL_AudioSpec fmt;

	if (argc>1)
		length = atoi (argv[1]);

// TODO: use 8bit audio here. fuck yeah
	/* Set 16-bit stereo audio at 22Khz */
	fmt.freq = 8000;
	fmt.format = AUDIO_S8;
	fmt.channels = 1;
	fmt.samples = 512;        /* A good value for games */
	fmt.callback = mixaudio;
	fmt.userdata = NULL;

	/* Open the audio device and start playing sound! */
	if (SDL_OpenAudio (&fmt, NULL) < 0) {
		fprintf (stderr, "Unable to open audio: %s\n", SDL_GetError());
		return 1;
	}
	// Load the audio data ... 
{
	audio_len = length;
	audio_chunk = malloc (audio_len);
	generate (0, audio_chunk, audio_len);
	audio_pos = audio_chunk;
}

	// Let the callback function play the audio chunk 
	SDL_PauseAudio (0);

	// Wait for sound to complete 
	while (audio_len > 0)
		SDL_Delay (100);         // Sleep 100 ms 

	SDL_CloseAudio (); 
	return 0;
}
