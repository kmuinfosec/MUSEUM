// Type your code here, or load an example.

#include <vector>
#include <string>
#include <fstream>
#define API __declspec(dllexport) // Windows-specific export

// Must pass double[4] array...
extern "C" API unsigned int ae_chunking(const char* buffer, unsigned long length, unsigned int** anchorArrPointer, const char* filePath, const unsigned int windowSize) {
	std::vector<unsigned int> anchorVec;
	unsigned int cursorIdx = 0;
	unsigned int lastCursorIdx = 0;
	int maxValue, maxIdx;
	while (cursorIdx < length) {
		maxValue = (unsigned char)buffer[cursorIdx];
		maxIdx = cursorIdx;
		cursorIdx++;
		while (cursorIdx < length) {
			if ((unsigned char)buffer[cursorIdx] <= maxValue) {
				if (cursorIdx == maxIdx + windowSize) {
					anchorVec.push_back(cursorIdx);
					lastCursorIdx = cursorIdx;
					cursorIdx++;
					break;
				}
			}
			else {
				maxValue = (unsigned char)buffer[cursorIdx];
				maxIdx = cursorIdx;
			}
			cursorIdx++;
		}
	}
	if (lastCursorIdx != cursorIdx) {
		anchorVec.push_back(cursorIdx);
	}
	unsigned int* anchorArr = (unsigned int*)malloc(sizeof(unsigned int) * anchorVec.size());
	for (auto it = anchorVec.begin(); it != anchorVec.end(); it++) {
		anchorArr[std::distance(anchorVec.begin(), it)] = *it;
	}
	*anchorArrPointer = anchorArr;
	return anchorVec.size();
}

extern "C" API void release(unsigned int* anchorArrPointer) {
	free(anchorArrPointer);
}