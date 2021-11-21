#include <vector>
#include <string>
#include <fstream>

bool ReadFile(std::string filePath, unsigned char **_data, unsigned int *datalen)
{
	std::ifstream is(filePath, std::ifstream::binary);
	if (is) {
		// seekg를 이용한 파일 크기 추출
		is.seekg(0, is.end);
		int length = (int)is.tellg();
		is.seekg(0, is.beg);

		// malloc으로 메모리 할당
		unsigned char * buffer = (unsigned char*)malloc(length);

		// read data as a block:
		is.read((char*)buffer, length);
		is.close();
		*_data = buffer;
		*datalen = length;
	}

	return true;
}


extern "C" unsigned int ae_chunking_from_path(const char* filePath, unsigned int** anchorArrPointer, const unsigned int windowSize) {
    unsigned char* buffer;
    unsigned int length;
    ReadFile(std::string(filePath), &buffer, &length);

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


extern "C" unsigned int ae_chunking_from_bytes(const unsigned char* buffer, unsigned int length, unsigned int** anchorArrPointer, const unsigned int windowSize) {
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

extern "C" void release(unsigned int* anchorArrPointer) {
	free(anchorArrPointer);
}